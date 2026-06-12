import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime, timezone
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

BASE_URL = "https://razgradnews.net"

BLOCKED_LINKS = [
    "kategoria",
    "reklama",
    "izprati-novina",
    "za-nas",
    "usloviya-za-polzvane",
    "kontakti",
    "feed",
    "cookie-policy",
    "plateni-reportaji",
    "oferta-za-reklama",
    "author/",
    "izbori-2026",
    "novini-ot-razgrad",
    "oblastta",
    "bulgaria",
    "podkasti",
    "sport-v-razgrad",
    "ludogorets",
    "lyubopitno",
    "glasat-na-razgrad",
    "svyat",
]

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
        "url": "https://razgradnews.net/novini-ot-razgrad",
        "category": "razgrad"
    },
    {
        "url": "https://razgradnews.net/novini-ot-razgrad/predstoyashto",
        "category": "predstoyashto"
    },
    {
        "url": "https://razgradnews.net/novini-ot-razgrad/kriminalni-novini-razgrad",
        "category": "kriminalni"
    },
    {
        "url": "https://razgradnews.net//novini-ot-razgrad/intsidenti",
        "category": "intsidenti"
    },
    {
        "url": "https://razgradnews.net/oblastta",
        "category": "oblastta"
    },
    {
        "url": "https://razgradnews.net/bulgaria",
        "category": "bulgaria"
    },
    {
        "url": "https://razgradnews.net/podkasti",
        "category": "podkasti"
    },
    {
        "url": "https://razgradnews.net/sport-v-razgrad",
        "category": "sport"
    },
    {
        "url": "https://razgradnews.net/ludogorets",
        "category": "ludogorets"
    },
    {
        "url": "https://razgradnews.net/lyubopitno",
        "category": "lyubopitno"
    },
    {
        "url": "https://razgradnews.net/glasat-na-razgrad",
        "category": "glasat_na_razgrad"
    },
    {
        "url": "https://razgradnews.net/svyat",
        "category": "svyat"
    },
    {
        "url": "https://razgradnews.net/oblastta/zavet",
        "category": "zavet"
    },
    {
        "url": "https://razgradnews.net/oblastta/isperih",
        "category": "isperih"
    },
    {
        "url": "https://razgradnews.net/oblastta/kubrat",
        "category": "kubrat"
    },
    {
        "url": "https://razgradnews.net/oblastta/loznitsa",
        "category": "loznitsa"
    },
    {
        "url": "https://razgradnews.net/oblastta/samuil",
        "category": "samuil"
    },
    {
        "url": "https://razgradnews.net/oblastta/tsar-kaloyan",
        "category": "tsar-kaloyan"
    }
]


def scrape_source(source):
    url = source["url"]
    category = source["category"]

    response = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")

    #Изтриване на старите записи за всяка категория във вече съществуващата база данни
    collection.delete_many({"category": category})

    found = 0
    rank = 0
    limit = 10
    if category == "homepage":
        limit = 9

    seen = set()

    content_root = soup.find("main") or soup.find(id="content") or soup

    if category == "homepage":
        elements = soup.find_all("a")
    else:
        elements = content_root.select("h2 a, h3 a")

    if len(elements) == 0:
        elements = soup.find_all("a")

    for a in elements:
        title = a.get_text(strip=True)
        link = a.get("href")
        
        if not title or not link:
            continue

        if title.lower() in [
        "новини",
        ]:
            continue

        if "author/" in link:
            continue

        if link.startswith("/"):
            link = BASE_URL + link

        if not link.startswith(BASE_URL + "/"):
            continue

        path = link.replace(BASE_URL + "/", "").strip("/")

        if not path:
            continue

        #махаме query параметри, ако има
        path = link.replace(BASE_URL + "/", "").strip("/")
        path = path.split("?")[0].split("#")[0]

        #пропускаме служебни страници и меню категории
        if any(path.startswith(blockedLink) for blockedLink in BLOCKED_LINKS):
            continue

        #пропускаме категории/подкатегории/архиви без конкретна статия
        if path in [
            "novini-ot-razgrad",
            "novini-ot-razgrad/kriminalni-novini-razgrad",
            "novini-ot-razgrad/intsidenti",
            "novini-ot-razgrad/institucii-v-razgrad",
            "novini-ot-razgrad/predstoyashto",
            "novini-ot-razgrad/biznes-v-razgrad",
            "oblastta",
            "oblastta/zavet",
            "oblastta/isperih",
            "oblastta/kubrat",
            "oblastta/loznitsa",
            "oblastta/samuil",
            "oblastta/tsar-kaloyan",
            "bulgaria",
            "podkasti",
            "podkasti/razgrad-podcast",
            "podkasti/mladite-v-sveta-na-vazrastnite",
            "podkasti/east-cast",
            "podkasti/obrazovanieto-otvatre",
            "sport-v-razgrad",
            "ludogorets",
            "lyubopitno",
            "glasat-na-razgrad",
            "svyat",
        ]:
            continue

        #уникализиране на линковете за страницата
        if link in seen:
            continue
        seen.add(link)
        #rank по уникални линкове
        rank += 1

        collection.update_one(
            {"url": link, "category": category},
            {"$set": {
                "title": title,
                "url": link,
                "category": category,
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