import threading
from pathlib import Path

from flask import Blueprint, current_app, jsonify, request

from api.auth import jwt_required
from api.repositories.book_repository import BookRepository
from scripts.scraper import BookScraper
from scripts.writer import CSVWriter

book_bp = Blueprint("books", __name__, url_prefix="/api/v1")


@book_bp.route("/books", methods=["GET"])
def get_books():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 25, type=int)

    repository = BookRepository()
    pagination = repository.get_all_paginated(page, per_page)

    return (
        jsonify(
            {
                "books": [
                    {
                        "id": b.id,
                        "title": b.title,
                        "price": b.price / 100,
                        "currency": b.currency,
                        "rating": b.rating,
                        "category": b.category,
                        "img_url": b.img_url,
                        "url": b.url,
                    }
                    for b in pagination.items
                ],
                "meta": {
                    "page": pagination.page,
                    "per_page": pagination.per_page,
                    "total_pages": pagination.pages,
                    "total_items": pagination.total,
                    "has_next": pagination.has_next,
                    "has_prev": pagination.has_prev,
                },
            }
        ),
        200,
    )


@book_bp.route("/books/search", methods=["GET"])
def search_books():
    title = request.args.get("title", type=str)
    category = request.args.get("category", type=str)
    min_rating = request.args.get("min_rating", type=float)
    max_price = request.args.get("max_price", type=float)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 25, type=int)

    if not any([title, category, min_rating, max_price]):
        return (
            jsonify(
                {
                    "error": "At least one search parameter is required (title, category, min_rating, max_price)"
                }
            ),
            400,
        )

    repository = BookRepository()
    pagination = repository.search(
        title=title,
        category=category,
        min_rating=min_rating,
        max_price=max_price,
        page=page,
        per_page=per_page,
    )

    return (
        jsonify(
            {
                "books": [
                    {
                        "id": b.id,
                        "title": b.title,
                        "price": b.price / 100,
                        "currency": b.currency,
                        "rating": b.rating,
                        "category": b.category,
                        "img_url": b.img_url,
                        "url": b.url,
                    }
                    for b in pagination.items
                ],
                "meta": {
                    "page": pagination.page,
                    "per_page": pagination.per_page,
                    "total_pages": pagination.pages,
                    "total_items": pagination.total,
                    "has_next": pagination.has_next,
                    "has_prev": pagination.has_prev,
                },
            }
        ),
        200,
    )


@book_bp.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id: int):
    repository = BookRepository()
    b = repository.get_by_id(book_id)

    if not b:
        return jsonify({"error": "Book not found"}), 404

    return (
        jsonify(
            {
                "id": b.id,
                "title": b.title,
                "price": b.price / 100,
                "currency": b.currency,
                "rating": b.rating,
                "category": b.category,
                "img_url": b.img_url,
                "url": b.url,
            }
        ),
        200,
    )


@book_bp.route("/categories", methods=["GET"])
def get_categories():
    repository = BookRepository()
    categories = repository.list_categories()
    return jsonify({"categories": categories}), 200


@book_bp.route("/health", methods=["GET"])
def health():
    repository = BookRepository()
    db_ok = repository.is_db_connected()

    status = "healthy" if db_ok else "unhealthy"
    code = 200 if db_ok else 500

    return (
        jsonify(
            {"status": status, "database": "connected" if db_ok else "disconnected"}
        ),
        code,
    )


# Admin scraping trigger
scraping_lock = threading.Lock()
scraping_in_progress = False


@book_bp.route("/scraping/trigger", methods=["POST"])
@jwt_required
def trigger_scraping():
    """Start the scraping pipeline in a background thread. Returns 202 if started,
    409 if a scraping job is already running.
    """
    if not scraping_lock.acquire(blocking=False):
        return (
            jsonify({"status": "busy", "message": "Scraping already in progress"}),
            409,
        )

    # capture app for logging inside background thread
    app = current_app._get_current_object()

    def worker(app=app):
        global scraping_in_progress
        try:
            scraping_in_progress = True

            fieldnames = [
                "title",
                "price",
                "currency",
                "rating",
                "category",
                "img_url",
                "url",
            ]

            try:
                with CSVWriter("./data/books.csv", fieldnames) as writer:
                    writer.save_header()
                    scraper = BookScraper(storage=writer)
                    scraper.run()
            except Exception:
                app.logger.exception("Scraper execution failed")

        finally:
            scraping_in_progress = False
            try:
                scraping_lock.release()
            except RuntimeError:
                pass

    th = threading.Thread(target=worker, daemon=True)
    th.start()

    return jsonify({"status": "started"}), 202


@book_bp.route("/scraping/trigger/status", methods=["GET"])
@jwt_required
def scraping_trigger_status():
    """Return scraping trigger status."""
    return (
        jsonify(
            {
                "running": bool(scraping_in_progress),
                "locked": scraping_lock.locked(),
            }
        ),
        200,
    )


@book_bp.route("/scraping/import/status", methods=["GET"])
@jwt_required
def scraping_import_status():
    """Return import status."""
    return (
        jsonify(
            {
                "running": bool(import_in_progress),
                "locked": import_lock.locked(),
            }
        ),
        200,
    )


import_lock = threading.Lock()
import_in_progress = False


@book_bp.route("/scraping/import", methods=["POST"])
@jwt_required
def trigger_import():
    """Import existing CSV data into the database in a background thread.
    Returns 202 if import started, 409 if import already running, or 400 if CSV missing.
    """
    CSV_PATH = Path("/app/data/books.csv")

    if not CSV_PATH.exists():
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"CSV file not found at {CSV_PATH}. Run scraper first.",
                }
            ),
            400,
        )

    if not import_lock.acquire(blocking=False):
        return jsonify({"status": "busy", "message": "Import already in progress"}), 409

    app = current_app._get_current_object()

    def worker(app=app):
        global import_in_progress
        try:
            import_in_progress = True
            with app.app_context():
                from api.services.book_import_service import BookImportService

                repository = BookRepository()
                service = BookImportService(repository)

                result = service.import_from_csv(CSV_PATH)
                app.logger.info(
                    "Import finished: inserted=%s skipped=%s",
                    result["inserted"],
                    result["skipped"],
                )
        except Exception:
            app.logger.exception("Import failed")
        finally:
            import_in_progress = False
            try:
                import_lock.release()
            except RuntimeError:
                pass

    th = threading.Thread(target=worker, daemon=True)
    th.start()

    return jsonify({"status": "started"}), 202
