import math
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from pymongo import MongoClient
from text_processor import build_inverted_index, build_tfidf_matrix, search_query

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


# # Retrieve HTML content
# def retrieve_html(url):
#     try:
#         response = requests.get(url, verify=True, timeout=10)  # Added timeout
#         response.raise_for_status()  # Raise exception for 4xx/5xx errors
#         return response.text
#     except requests.exceptions.HTTPError as e:
#         print(f"HTTP Error: {e}")
#     except requests.exceptions.SSLError as e:
#         print(f"SSL Error: {e}")
#     except requests.exceptions.RequestException as e:
#         print(f"Request Error: {e}")
#     return ''  # Return empty string for failed requests

# # Crawl pages and process data
# def crawl_pages(seed_url, pages_collection, faculty_collection, num_targets):
#     visited_urls = set()
#     frontier = [seed_url]
#     targets_found = 0

#     while frontier and targets_found < num_targets:
#         url = frontier.pop(0)
#         if url in visited_urls:
#             continue

#         html = retrieve_html(url)
#         if not html:
#             continue

#         is_target = bool(BeautifulSoup(html, 'html.parser').find(attrs={'class': 'fac-info'}))
#         pages_collection.insert_one({"url": url, "html": html, "targetPage": 1 if is_target else 0})

#         if is_target:
#             soup = BeautifulSoup(html, 'html.parser')
#             fac_main = soup.select_one('div.fac.main').get_text(strip=True) if soup.select_one('div.fac.main') else ''
#             fac_right = soup.select_one('aside.fac.rightcol').get_text(strip=True) if soup.select_one('aside.fac.rightcol') else ''
#             faculty_collection.insert_one({"url": url, "fac_main": fac_main, "fac_right": fac_right})
#             targets_found += 1

#         visited_urls.add(url)

#         soup = BeautifulSoup(html, 'html.parser')
#         for link in soup.find_all('a', href=True):
#             abs_url = urljoin(seed_url, link['href'])
#             if abs_url.startswith('mailto:') or not abs_url.startswith(('http://', 'https://')):
#                 continue
#             if abs_url not in visited_urls:
#                 frontier.append(abs_url)

#     print(f"Crawling completed. Found {targets_found} target pages.")

# Main function
def main():
    # Connect to MongoDB Atlas
    # db = connect_to_atlas()

    # Connect to MongoDB Compass
    db = connect_to_compass()


    print('Connecting to collection: faculty_websites')
    faculty_websites = db["faculty_websites"]


    faculty_data = list(faculty_websites.find())
    # print(faculty_data)
    inverted_index = build_inverted_index(faculty_data, db)
    print("Inverted index built successfully!")

    vectorizer, tfidf_matrix = build_tfidf_matrix(faculty_data)
    print("TF-IDF matrix built successfully! Search engine ready.")

    while True:
        query = input("Enter your search query (or 'exit' to quit): ").strip()
        if query.lower() == "exit":
            break

        page = 1
        while True:
            results, total = search_query(query, vectorizer, tfidf_matrix, faculty_data, inverted_index, page=page)
            if not results:
                print("No results found.")
                break

            print(f"\nPage {page} of {math.ceil(total / 5)}:")
            for i, result in enumerate(results, start=1):
                score = result['score']
                print(f"{i}. {result['url']}")
                print(f"Score: {score:.2f}")
                print(f"Snippet: {result['snippet']}...\n")

            nav = input("Enter 'n' for next page, 'p' for previous page, or 'q' to quit: ").strip().lower()
            if nav == "n":
                page += 1
            elif nav == "p" and page > 1:
                page -= 1
            elif nav == "q":
                break

if __name__ == "__main__":
    main()