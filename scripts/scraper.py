from writer import CSVWriter
from storageInterface import DataStorage
from bs4 import BeautifulSoup
import requests
import re

class BookScraper():
    def __init__(self, storage: DataStorage):
        self.base_url = "https://books.toscrape.com/catalogue/"
        self.start_url = f"{self.base_url}page-1.html"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
        }
        self.last_page = 0
        self._books_urls = list()
        self.storage = storage

    def get_soup(self, url):
        """
        método auxiliar para evitar repetição de código de request
        """
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            raise Exception(f"Erro ao acessar {url}: Status {response.status_code}")
        
        return BeautifulSoup(response.content, 'html.parser')

    def set_last_page_number(self):
        """
        Extrai o número da última página
        """
        soup = self.get_soup(self.start_url)
        
        pager = soup.find('ul', class_='pager')
        
        text = pager.text.strip()
        
        match = re.search(r"of\s+(\d+)", text)
        
        if match:
            self.last_page = int(match.group(1))
            print(f"Total de páginas identificadas: {self.last_page}")
    
    def get_all_books_urls(self):
        for i in range(1, self.last_page + 1):
            url = f"{self.base_url}page-{i}.html"
            soap = self.get_soup(url)
            
            books = soap.find_all("article", class_="product_pod")
            
            for book in books:
                tag_a = book.h3.a
                
                relative_url = tag_a['href']

                self._books_urls.append(relative_url)
        
    def run(self):
        """
        Fluxo principal de execução
        """
        self.set_last_page_number()
        self.get_all_books_urls()
        
        print(self._books_urls)
        
if __name__ == "__main__":
    filename = "./data/book_data"
    fieldnames = ["title", "price", "rating", "category", "img_url"]
        
    scraper = BookScraper(CSVWriter(
       filename,
       fieldnames
    ))
    
    scraper.run()
