from pymongo import MongoClient
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

def connect_to_atlas():
    """
    Connect to MongoDB Atlas.
    """
    print('Connecting to MongoDB Atlas...')

    connection_string = "mongodb+srv://rash30star:workworkwork@myfirstcluster.ntntd.mongodb.net/CPPCivilEngineering?retryWrites=true&w=majority"
    DB_NAME = "CPPCivilEngineering"
    try:
        client = MongoClient(connection_string)
        db = client[DB_NAME]
        print("Connected to MongoDB Atlas")
        return db
    except Exception as e:
        print("Error connecting to MongoDB Atlas:", e)
        return None

def connect_to_compass():
    """
    Connect to MongoDB Compass.
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


def index_documents(db):
    """
    Index all faculty pages into a list for processing with TF-IDF.
    """
    pages = db["faculty_websites"].find()  # Collection containing faculty pages
    documents = []
    urls = []
    for page in pages:
        html = page["fac_main"] + page["fac_right"]
        text = preprocess_html(html)
        documents.append(text)
        urls.append(page["url"])
    return documents, urls


def search_query(query, vectorizer, tfidf_matrix, documents, urls, page=1, results_per_page=5):
    """
    Search for a query and return paginated results.
    """
    query_vector = vectorizer.transform([query])
    similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()

    # Sort by similarity score
    ranked_indices = similarities.argsort()[::-1]
    ranked_documents = [(urls[i], documents[i], similarities[i]) for i in ranked_indices]

    # Paginate results
    start = (page - 1) * results_per_page
    end = start + results_per_page
    paginated_results = ranked_documents[start:end]

    return paginated_results


def display_results(results):
    """
    Display the search results.
    """
    for i, (url, snippet, score) in enumerate(results):
        if score > 0:
            print(f"Result {i + 1}:")
            print(f"URL: {url}")
            print(f"Score: {score:.2f}")
            print(f"Snippet: {snippet[:200]}...")  
            print("=" * 80)


def main():
    # Connect to MongoDB Atlas
    # db = connect_to_atlas()

    # Connect to MongoDB Compass
    db = connect_to_compass()


    documents, urls = index_documents(db)

    vectorizer = TfidfVectorizer(stop_words="english", max_features=1000)
    tfidf_matrix = vectorizer.fit_transform(documents)

    print("Search engine is ready!")

    while True:
        query = input("Enter your search query (or type 'exit' to quit): ").strip()
        if query.lower() == "exit":
            break

        page = 1
        while True:
            results = search_query(query, vectorizer, tfidf_matrix, documents, urls, page)

            if not results:
                print("No results found.")
                break

            print(f"Page {page}:")
            display_results(results)

            next_page = input("Type 'n' for next page, 'b' for previous page, or 'q' to quit: ").strip().lower()
            if next_page == "n":
                page += 1
            elif next_page == "b" and page > 1:
                page -= 1
            elif next_page == "q":
                break
            else:
                print("Invalid input. Returning to query menu.")
                break


if __name__ == "__main__":
    main()
