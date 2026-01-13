from pathlib import Path

from api.main import create_app
from api.repositories.book_repository import BookRepository
from api.services.book_import_service import BookImportService


CSV_PATH = Path("data/book_data.csv")


def main() -> None:
    app = create_app()

    with app.app_context():
        repository = BookRepository()
        service = BookImportService(repository)

        result = service.import_from_csv(CSV_PATH)

        print(f"✅ Inserted: {result['inserted']}")
        print(f"⏭️  Ignored (duplicates): {result['skipped']}")


if __name__ == "__main__":
    main()
