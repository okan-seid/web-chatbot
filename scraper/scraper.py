import requests
import re
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime, timezone
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

BASE_URL = "https://razgradnews.net"

#Локална база MongoDB
#client = MongoClient("mongodb://localhost:27017/")

#Онлайн база MongoDB Atlas
client = MongoClient(MONGO_URI)
db = client["web-chatbot"]
collection = db["news"]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

#Категории и техните url-и в сайта
SOURCES = [
    {
        "url": "https://razgradnews.net/",
        "category": "homepage"
    },
    {
        "url": "https://razgradnews.net/kategoria/novini-ot-razgrad",
        "category": "razgrad"
    },
    {
        "url": "https://razgradnews.net/kategoria/novini-ot-razgrad/predstoyashto",
        "category": "predstoyashto"
    },
    {
        "url": "https://razgradnews.net/kategoria/novini-ot-razgrad/kriminalni-novini-razgrad",
        "category": "kriminalni"
    },
    {
        "url": "https://razgradnews.net/kategoria/novini-ot-razgrad/intsidenti",
        "category": "intsidenti"
    },
    {
        "url": "https://razgradnews.net/kategoria/oblastta",
        "category": "oblastta"
    },
    {
        "url": "https://razgradnews.net/kategoria/bulgaria",
        "category": "bulgaria"
    },
    {
        "url": "https://razgradnews.net/kategoria/podkasti",
        "category": "podkasti"
    },
    {
        "url": "https://razgradnews.net/kategoria/sport-v-razgrad",
        "category": "sport"
    },
    {
        "url": "https://razgradnews.net/kategoria/lyubopitno",
        "category": "lyubopitno"
    },
    {
        "url": "https://razgradnews.net/kategoria/glasat-na-razgrad",
        "category": "glasat_na_razgrad"
    },
    {
        "url": "https://razgradnews.net/kategoria/svyat",
        "category": "svyat"
    }
]


def scrape_source(source):
    url = source["url"]
    category = source["category"]

    response = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")

    found = 0
    rank = 0
    limit = None
    if category == "homepage":
        limit = 13

    seen = set()

    content_root = soup.find("main") or soup.find(id="content") or soup

    if category == "homepage":
        elements = soup.find_all("a")
    else:
        elements = content_root.select("h2 a, h3 a")

    for a in elements:
        title = a.get_text(strip=True)
        link = a.get("href")
        
        if not title or not link:
            continue

        if link.startswith("/"):
            link = BASE_URL + link

        #допускаме само статии /YYYY/MM/DD/
        if not re.search(r"^https://razgradnews\.net/\d{4}/\d{2}/\d{2}/", link):
            continue

        #уникализиране на линковете за страницата
        if link in seen:
            continue
        seen.add(link)

        #rank по уникални линкове
        rank += 1


        #извличаме published_at от URL (ден в UTC)
        m = re.search(r"^https://razgradnews\.net/(\d{4})/(\d{2})/(\d{2})/", link)
        published_at = None
        if m:
            y, mo, d = m.groups()
            published_at = datetime(int(y), int(mo), int(d), tzinfo=timezone.utc)

        collection.update_one(
            {"url": link, "category": category},
            {"$set": {
                "title": title,
                "url": link,
                "category": category,
                "published_at": published_at,
                "scraped_at": datetime.now(timezone.utc),
                "rank": rank
            }},
            upsert=True
        )

        found += 1

        #ако сме на homepage и стигнем лимита – спиране
        if limit is not None and rank >= limit:
            break


    print(f"{category}: намерени {found} новини")

def run():
    for source in SOURCES:
        scrape_source(source)

if __name__ == "__main__":
    run()