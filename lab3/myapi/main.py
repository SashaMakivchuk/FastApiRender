from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import datetime

app = FastAPI()

# модель для зібраних даних
class ScrapedData(BaseModel):
    title: str
    url: str
    content: str
    scraped_at: datetime.datetime

# тимчасове сховище (можна замінити на базу пізніше)
database: List[ScrapedData] = []

@app.post("/submit")
async def submit_data(data: ScrapedData):
    print(f"Received: {data}")
    database.append(data)
    return {"message": "Data received successfully", "items_in_db": len(database)}

@app.get("/data")
async def get_all_data():
    return database
