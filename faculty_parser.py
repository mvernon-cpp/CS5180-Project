from urllib.request import urlopen
from bs4 import BeautifulSoup
from pymongo import MongoClient
import re

def main():

    # Connect to MongoDB Atlas
    # db = connect_to_atlas()

    # Connect to MongoDB Compass
    db = connect_to_compass()

    db["faculty_websites"].drop()

    pages = db["pages"]

    print('Connecting to collection: faculty_websites')
    faculty_websites = db["faculty_websites"]

    target_pages = findTargetPage(pages)

    for target_page in target_pages:
        if target_page is not None:
            html = target_page.get('html')
            url = target_page.get('url')

            parseFacultyWebsite(faculty_websites, html, url)
        else:
            print('Target page does not exist.')

def connect_to_compass():
    """
    Connects to MongoDB Compass
    """
    print('Connecting to MongoDB Compass...')

    DB_NAME = "CPPCivilEngineering"
    DB_HOST = "localhost"
    DB_PORT = 27017

    try:
        client = MongoClient(host=DB_HOST, port=DB_PORT)
        db = client[DB_NAME]

        return db
    except:
        print("Database not connected successfully")


def connect_to_atlas():
    """
    Connects to MongoDB Atlas using the correct connection string.
    """
    print('Connecting to MongoDB Atlas...')

    # MongoDB Atlas connection string
    connection_string = (
        "mongodb+srv://rash30star:workworkwork@myfirstcluster.ntntd.mongodb.net/CPPCivilEngineering?retryWrites=true&w=majority"
    )

    DB_NAME = "CPPCivilEngineering"

    try:
        client = MongoClient(connection_string)
        db = client[DB_NAME]
        print("Connected to MongoDB Atlas successfully")
        return db
    except Exception as e:
        print("Error connecting to MongoDB Atlas:", e)
        return None


def findTargetPage(pages):
    """
    Finds all target pages where "targetPage" is 1.
    """
    return pages.find({"targetPage": 1})


def parseFacultyWebsite(faculty_websites, html, url):
    """
    Parses faculty websites and stores the main and right column HTML in MongoDB.
    """
    bs = BeautifulSoup(html, 'html.parser')

    fac_main = bs.select('div.fac.main')
    fac_right = bs.select('aside.fac.rightcol')

    if fac_main and fac_right:
        main_text = preprocess_html(fac_main[0].get_text())
        right_text = preprocess_html(fac_right[0].get_text())
        storeFacultyWebsites(faculty_websites, url, main_text, right_text)
    else:
        print(f"Could not find 'fac.main' or 'fac.rightcol' sections for URL: {url}")


def storeFacultyWebsites(faculty_websites, url, fac_main, fac_right):
    """
    Stores the parsed faculty website sections in the faculty_websites collection.
    """
    website = {
        "url": url,
        "fac_main": fac_main,
        "fac_right": fac_right,
    }

    faculty_websites.insert_one(website)
    print("Stored:", url)
    print('=' * 100)

def preprocess_html(html):
    """
    Extract and clean text from HTML content.
    """
    soup = BeautifulSoup(html, "html.parser")
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.extract()
    text = soup.get_text()
    text = re.sub(r"\s+", " ", text).strip()
    return text

if __name__ == '__main__':
    main()
