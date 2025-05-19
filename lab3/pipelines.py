# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import mysql.connector
import re
import requests
from datetime import datetime



class SaveToDatabasePipeline:
    def open_spider(self, spider):
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="scrapy"
            )
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS items (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255),
                    price VARCHAR(50),
                    url TEXT,
                    image TEXT
                )
            ''')
            self.conn.commit()
            print("Database connection successful!")
        except mysql.connector.Error as err:
            print(f"Error: {err}")

    def process_item(self, item, spider):
        if not hasattr(self, 'cursor'):
            print("Error: Database cursor is not initialized.")
            return item


        try:
            self.cursor.execute('''
                INSERT INTO items (name, price, url, image)
                VALUES (%s, %s, %s, %s)
            ''', (
            item.get("name"), item.get("price"), item.get("url"), ",".join(item.get("image_urls", []))))
            self.conn.commit()
            print("Item saved to database!")
        except mysql.connector.Error as err:
            print(f"Error saving item to database: {err}")

        return item

    def close_spider(self, spider):
        if hasattr(self, 'conn'):
            self.conn.close()

class Lab3Pipeline:
    def process_item(self, item, spider):
        data = {
            "title": item.get("name"),
            "url": item.get("url"),
            "content": f"Ціна: {item.get('price')}",
            "scraped_at": datetime.utcnow().isoformat()
        }

        try:
            response = requests.post("http://localhost:8000/submit", json=data)
            if response.status_code == 200:
                spider.logger.info("✅ Дані успішно відправлено на API")
            else:
                spider.logger.warning(f"❌ Помилка при надсиланні: {response.status_code} {response.text}")
        except Exception as e:
            spider.logger.error(f"🔥 Виняток при відправці: {e}")

        return item

class DataCleaningPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if adapter.get("name"):
            adapter["name"] = adapter["name"].strip()

        if adapter.get("price"):
            price = adapter["price"].strip()

            price = re.sub(r'[^\d.,]', '', price)
            price = price.replace(",", "")
            price = price.replace(".", "")
            adapter["price"] = price

        return item
