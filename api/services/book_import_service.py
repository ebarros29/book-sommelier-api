import csv
from pathlib import Path
from typing import List

from api.models.book import Book
from api.repositories.book_repository import BookRepository


class BookImportService:
    def __init__(self, repository: BookRepository):
        self.repository = repository

    def import_from_csv(self, csv_path: str | Path) -> dict:
        books = self._load_csv(csv_path)
        existing_urls = self.repository.get_existing_urls()

        to_insert = [
            book for book in books
            if book.url not in existing_urls
        ]

        self.repository.bulk_insert(to_insert)

        return {
            "inserted": len(to_insert),
            "skipped": len(books) - len(to_insert)
        }

    def _load_csv(self, csv_path: str | Path) -> List[Book]:
        books: List[Book] = []

        with open(csv_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                books.append(self._parse_row(row))

        return books

    def _parse_row(self, row: dict) -> Book:
        try:
            return Book(
                title=row["title"].strip(),
                price=int(row["price"]),
                currency=row.get("currency", "GBP"),
                rating=float(row["rating"]) if row.get("rating") else None,
                category=row.get("category"),
                img_url=row.get("img_url"),
                url=row["url"].strip(),
            )
        except (KeyError, ValueError) as exc:
            raise ValueError(f"Error processing CSV line: {row}") from exc
