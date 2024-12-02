import math
from urllib.parse import urljoin
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


# Main function
def main():
    # Connect to MongoDB Atlas
    # db = connect_to_atlas()

    # Connect to MongoDB Compass
    db = connect_to_compass()


    print('Connecting to collection: faculty_websites')
    faculty_websites = db["faculty_websites"]


    faculty_data = list(faculty_websites.find())
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