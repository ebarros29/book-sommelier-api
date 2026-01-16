from flask import Blueprint, jsonify, request

from api.repositories.book_repository import BookRepository

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
