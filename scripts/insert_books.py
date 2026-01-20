import os
import sys
from pathlib import Path
from api.main import create_app
from api.repositories.book_repository import BookRepository
from api.services.book_import_service import BookImportService

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "books.csv"

def main() -> None:
    if not CSV_PATH.exists():
        print(f"Skip: File '{CSV_PATH}' not found. Scraping needed.")
        sys.exit(0)
        
    app = create_app()

    with app.app_context():
        repository = BookRepository()
        service = BookImportService(repository)

        result = service.import_from_csv(CSV_PATH)

        print(f"✅ Inserted: {result['inserted']}")
        print(f"⏭️  Ignored (duplicates): {result['skipped']}")


if __name__ == "__main__":
    main()
