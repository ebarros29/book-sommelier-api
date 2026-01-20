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
        # If CSV is missing, either auto-run the scraper (if AUTO_SCRAPE=1)
        # or skip import gracefully and instruct the operator.
        if not CSV_PATH.exists():
            auto_scrape = os.getenv("AUTO_SCRAPE", "0") in ("1", "true", "True")

            if auto_scrape:
                # Run the scraper to generate the CSV before importing
                from scripts.scraper import BookScraper
                from scripts.writer import CSVWriter

                fieldnames = [
                    "title",
                    "price",
                    "currency",
                    "rating",
                    "category",
                    "img_url",
                    "url",
                ]
                print(
                    f"CSV not found at {CSV_PATH}. AUTO_SCRAPE is enabled — running scraper..."
                )
                with CSVWriter(str(CSV_PATH), fieldnames) as writer:
                    writer.save_header()
                    scraper = BookScraper(storage=writer)
                    scraper.run()
            else:
                print(f"CSV file not found: {CSV_PATH}")
                print("To auto-generate the CSV at startup set AUTO_SCRAPE=1,")
                print(
                    "or trigger scraping via POST /api/v1/scraping/trigger and then run the import manually."
                )
                return

        repository = BookRepository()
        service = BookImportService(repository)

        result = service.import_from_csv(CSV_PATH)

        print(f"✅ Inserted: {result['inserted']}")
        print(f"⏭️  Ignored (duplicates): {result['skipped']}")


if __name__ == "__main__":
    main()
