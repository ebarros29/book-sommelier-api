import csv
import os

from scripts.storageInterface import DataStorage


class CSVWriter(DataStorage):
    def __init__(self, filename: str, fieldnames: list):
        if not filename.endswith(".csv"):
            filename += ".csv"
        self.filename = filename
        self.fieldnames = fieldnames
        self._file = None
        self._writer = None
        self._prepare_directory()

    def _prepare_directory(self):
        directory = os.path.dirname(self.filename)
        if directory:
            os.makedirs(directory, exist_ok=True)

    def __enter__(self):
        self._file = open(self.filename, "w", newline="", encoding="utf-8")
        self._writer = csv.DictWriter(self._file, fieldnames=self.fieldnames)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._file:
            self._file.close()

    def save_header(self):
        if self._writer:
            self._writer.writeheader()

    def save_item(self, data):
        if self._writer:
            self._writer.writerow(data)
