import scrapy
from bs4 import BeautifulSoup
from lab3.items import Lab3Item

class PhonesSpider(scrapy.Spider):
    name = "phones"
    allowed_domains = ["allo.ua", "localhost"]
    start_urls = [f"https://allo.ua/ua/products/mobile/p-{page}/" for page in range(1, 5)]
    API_URL = "https://localhost:8000/submit/"

    def parse(self, response):
        soup = BeautifulSoup(response.text, "html.parser")

        # Знаходимо всі товари
        products = soup.select("div.product-card")

        if not products:
            self.logger.warning("Не знайдено жодного товару на сторінці!")

        for product in products:
            # Назва товару
            name = product.select_one("a.product-card__title")
            name = name.get_text(strip=True) if name else None

            # URL сторінки товару
            url_tag = product.select_one("a.product-card__title")
            url = url_tag["href"] if url_tag else None
            if url and not url.startswith("http"):
                url = f"https://allo.ua{url}"

            # Ціна товару
            price = product.select_one("div.v-pb__cur")
            price = price.get_text(strip=True) if price else None

            # URL зображення
            image_tag = product.select_one("img.gallery__img")
            image_url = image_tag["src"] if image_tag else None
            if not image_url:
                image_url = image_tag["data-src"] if image_tag and image_tag.has_attr("data-src") else None
            if image_url and not image_url.startswith("http"):
                image_url = f"https://allo.ua{image_url}"

            yield Lab3Item(
                name=name,
                price=price,
                url=url,
                image_urls=[image_url] if image_url else []
            )
