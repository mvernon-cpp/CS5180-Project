from urllib.request import urlopen
from bs4 import BeautifulSoup
from pymongo import MongoClient
import urllib.parse



class Frontier:
    def __init__(self, startingUrl):
        self.urls = []
        self.urls.append(startingUrl)
        self.current_index = 0
        self.end = len(self.urls)

    def done(self):
        return self.current_index == self.end

    def nextURL(self):
        current_url = self.urls[self.current_index]
        self.current_index += 1
        return current_url

    def clear(self):
        print('Clearing frontier')
        self.current_index = 0
        self.end = 0
        self.urls.clear()

    def addURL(self, url):
        if url not in self.urls:
            self.urls.append(url)
            self.end += 1


def main():

    # Connect to MongoDB Atlas
    db = connect_to_atlas()

    # Connect to MongoDB Compass
    # db = connect_to_compass()

    pages = db["pages"]
    pages.drop()

    frontier = Frontier("https://www.cpp.edu/engineering/ce/index.shtml")
    num_target = 25

    crawlerThread(frontier, pages, num_target)


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


def retrieveHTML(url):
    """
    Retrieves the HTML content of a given URL.
    """
    try:
        html = urlopen(url)
    except Exception as e:
        print(f"Error retrieving URL {url}: {e}")
        return ""
    try:
        bs = BeautifulSoup(html.read(), "html.parser")
    except Exception as e:
        print(f"Error parsing HTML from URL {url}: {e}")
        return ""
    return bs.prettify()


def storePage(pages, url, html):
    """
    Stores the page HTML and metadata into the MongoDB Atlas collection.
    """
    page = {
        "url": url,
        "html": html,
        "targetPage": 0,
    }
    pages.insert_one(page)


def targetPage(html):
    """
    Determines if the HTML page is a target page by checking for specific elements.
    """
    bs = BeautifulSoup(html, "html.parser")
    return bool(bs.find(attrs={"class": "fac-info"}))


def flagTargetPage(pages, url):
    """
    Updates the MongoDB collection to mark a page as a target page.
    """
    pages.update_one({"url": url}, {"$set": {"targetPage": 1}})


def findURLs(html):
    """
    Finds all valid URLs in the given HTML.
    """
    ce_base = "https://www.cpp.edu/engineering/ce/"
    cpp_base = "http://www.cpp.edu"
    cpp_base_secure = "https://www.cpp.edu"

    urls = []
    bs = BeautifulSoup(html, "html.parser")
    contains_hrefs = bs.find_all(href=True)

    file_types = [".pdf", ".docx", ".doc", ".ppt", ".pptx", ".png", ".jpg", ".jpeg", ".ai", ".xlsx"]

    for hrefs in contains_hrefs:
        href = hrefs["href"].replace(" ", "")

        if any(ele in href for ele in file_types):
            continue
        elif "mailto" in href:
            continue
        elif cpp_base_secure in href or cpp_base in href:
            urls.append(href)
        elif "http" in href and cpp_base_secure not in href:
            continue
        elif cpp_base_secure not in href:
            urls.append(urllib.parse.urljoin(ce_base, href))
        else:
            continue

    sanitized_found_urls = [url for url in urls if cpp_base_secure in url]

    return sanitized_found_urls


def crawlerThread(frontier, pages, num_targets):
    """
    Implements the crawler logic strictly following the provided pseudocode.
    """
    targets_found = 0
    while not frontier.done():
        url = frontier.nextURL()
        print("Current URL:", url)

        html = retrieveHTML(url)
        storePage(pages, url, html)

        if targetPage(html):
            print("Target met, adding flag")
            flagTargetPage(pages, url)
            targets_found += 1

        if targets_found == num_targets:
            frontier.clear()
        else:
            print("Targets found:", targets_found)
            found_urls = findURLs(html)
            for found_url in found_urls:
                frontier.addURL(found_url)

    print("==========\nFinished crawler thread. Check MongoDB Atlas.\n==========")


if __name__ == "__main__":
    main()
