from writer import CSVWriter
from storageInterface import DataStorage
from bs4 import BeautifulSoup
from urllib.parse import urljoin
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
        Auxiliary method to avoid repeating request code.
        """
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            raise Exception(f"Erro ao acessar {url}: Status {response.status_code}")
        
        return BeautifulSoup(response.content, 'html.parser')

    def set_last_page_number(self):
        """
        Extract the number from the last page.
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
            soup = self.get_soup(url)
            
            books = soup.find_all("article", class_="product_pod")
            
            for book in books:
                tag_a = book.h3.a
                
                relative_url = tag_a['href']

                self._books_urls.append(relative_url)
    
    def _parse_price_string(self, price_raw: str):        
        currency_maps = {
            "£": "GBP",
            "€": "EUR",
            "$": "USD",
            "R$": "BRL"
        }
        
        match = re.search(r"([^0-9.Â]+)\s*([\d.]+)", price_raw)
        
        if match:
            currency_symbol = match.group(1).strip()
            price_value = float(match.group(2))
            
            currency_code = currency_maps.get(currency_symbol, "UNKNOWN")
            
            price_in_cents = int(round(price_value * 100))
            
            return currency_code, price_in_cents
        
        return "N/A", 0
    
    def _find_book_title(self, soup: BeautifulSoup):
        """
        Get the book title.
        """
        product_main = soup.find("div", class_="product_main")
        return product_main.h1.text.strip()
    
    def _find_book_price(self, soup: BeautifulSoup):
        """
        Get the price of the book.
        """
        price = soup.find("p", class_="price_color")
        return self._parse_price_string(price.text)
    
    def _find_book_rating(self, soup: BeautifulSoup):
        """
        Get the evaluation
        """
        rating_map = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5
        }
        
        tag_p = soup.find("p", class_="star-rating")
        
        if tag_p:
            classes = tag_p.get("class", [])
            
            for cls in classes:
                if cls in rating_map:
                    return rating_map[cls]
                
    def _find_book_category(self, soup: BeautifulSoup):
        """
        Get the category
        """
        
        breadcrumb = soup.find('ul', class_="breadcrumb")
        items = breadcrumb.find_all('li')
        
        return items[2].get_text(strip=True)
    
    def _find_book_image(self, soup: BeautifulSoup):
        """
        Get the image URL.
        """
        product_gallery = soup.find("div", id="product_gallery")
    
        if product_gallery:
            img_tag = product_gallery.find("img")
            
            if img_tag and img_tag.get("src"):
                relative_path = img_tag.get("src")
                
                full_image_url = urljoin(self.base_url, relative_path)
                
                return full_image_url
            
        return None

    def save_books(self):
        total = len(self._books_urls)
        for i, book_url in enumerate(self._books_urls, 1):
            soup = self.get_soup(urljoin(self.base_url, book_url))
            
            title = self._find_book_title(soup)
            currency, price = self._find_book_price(soup)
            rating = self._find_book_rating(soup)
            category = self._find_book_category(soup)
            img_url = self._find_book_image(soup)
            full_url = urljoin(self.base_url, book_url)
            
            data = {
                "title": title,
                "price": price,
                "currency": currency,
                "rating": rating,
                "category": category,
                "img_url": img_url,
                "url": full_url
            }
            
            print(f"[{i}/{total}] Processando: {title}")
            self.storage.save_item(data)
            
    def run(self):
        """
        Main execution flow
        """
        self.set_last_page_number()
        self.get_all_books_urls()
        self.save_books()
        
if __name__ == "__main__":
    filename = "./data/book_data"
    fieldnames = ["title", "price", "currency", "rating", "category", "img_url", "url"]
        
    with CSVWriter("./data/book_data", fieldnames) as writer:
        scraper = BookScraper(storage=writer)
        writer.save_header()
        scraper.run()
