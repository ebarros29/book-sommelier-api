import logging
from typing import Iterable, Optional, Set

from sqlalchemy import text

from api.extensions import db
from api.models.book import Book


class BookRepository:
    def get_all_paginated(self, page: int, per_page: int = 25):
        return Book.query.paginate(page=page, per_page=per_page, error_out=False)

    def search(
        self,
        title: Optional[str] = None,
        category: Optional[str] = None,
        min_rating: Optional[float] = None,
        max_price: Optional[float] = None,
        page: int = 1,
        per_page: int = 25,
    ):
        query = Book.query

        if title:
            query = query.filter(Book.title.ilike(f"%{title}%"))

        if category:
            query = query.filter(Book.category.ilike(f"%{category}%"))

        if min_rating is not None:
            query = query.filter(Book.rating >= min_rating)

        if max_price is not None:
            # Convert price to cents for comparison
            max_price_cents = int(max_price * 100)
            query = query.filter(Book.price <= max_price_cents)

        return query.paginate(page=page, per_page=per_page, error_out=False)

    def get_existing_urls(self) -> Set[str]:
        return {url for (url,) in db.session.query(Book.url).all()}

    def bulk_insert(self, books: Iterable[Book]) -> None:
        db.session.add_all(books)
        db.session.commit()

    def get_by_id(self, book_id: int) -> Optional[Book]:
        return Book.query.get(book_id)

    def list_categories(self) -> list[str]:
        rows = db.session.query(Book.category).distinct().order_by(Book.category).all()
        return [c for (c,) in rows if c]

    def is_db_connected(self) -> bool:
        try:
            with db.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception:
            logging.exception("Database health check failed")
            return False
