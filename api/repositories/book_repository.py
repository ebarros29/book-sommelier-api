from api.models.book import Book
from typing import Iterable, Set
from api.extensions import db

class BookRepository:
    def get_all_paginated(self, page: int, per_page: int = 25):
        return Book.query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
    
    def get_existing_urls(self) -> Set[str]:
        return {
            url for (url,) in db.session.query(Book.url).all()
        }

    def bulk_insert(self, books: Iterable[Book]) -> None:
        db.session.add_all(books)
        db.session.commit()