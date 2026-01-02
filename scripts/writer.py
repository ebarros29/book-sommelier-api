from storageInterface import DataStorage
import csv
import os

class CSVWriter(DataStorage):
    def __init__(self, filename: str, fieldnames: list):
        self.filename = filename
        self.fieldnames = fieldnames
        self._prepare_directory()
        
    def _prepare_directory(self):
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        
    def save_header(self):
        with open(self.filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writeheader()
            
    def save_item(self, data):
        with open(self.filename, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writerow(data)