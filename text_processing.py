import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict

# Configure NLTK to use a local directory
nltk.data.path.append('C:\\Users\\mzahi\\Github\\CS5180-Project\\nltk_data\\')
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab', download_dir='C:\\Users\\mzahi\\Github\\CS5180-Project\\nltk_data\\')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet', download_dir='C:\\Users\\mzahi\\Github\\CS5180-Project\\nltk_data\\')

try:
    nltk.data.find('corpora/omw-1.4')
except LookupError:
    nltk.download('omw-1.4', download_dir='C:\\Users\\mzahi\\Github\\CS5180-Project\\nltk_data\\')

# Initialize stemmer
stemmer = PorterStemmer()

def tokenize_and_stem(text):
    """Tokenize and stem the given text."""
    tokens = word_tokenize(text.lower())
    return [stemmer.stem(token) for token in tokens if token.isalnum()]

def build_inverted_index(faculty_data):
    """Build an inverted index from faculty data."""
    inverted_index = defaultdict(list)
    for doc_id, data in enumerate(faculty_data):
        combined_text = (data.get("fac_main", "") + " " + data.get("fac_right", "")).strip()
        tokens = tokenize_and_stem(combined_text)
        for token in set(tokens):  # Avoid duplicates
            inverted_index[token].append(doc_id)
    return inverted_index

def build_tfidf_matrix(faculty_data):
    """Build a TF-IDF matrix from faculty data."""
    documents = [f"{doc['fac_main']} {doc['fac_right']}" for doc in faculty_data]
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(documents)
    return vectorizer, tfidf_matrix

def search_query(query, vectorizer, tfidf_matrix, faculty_data, inverted_index, page=1, results_per_page=5):
    """Perform a search query using the Vector Space Model."""
    query_tokens = tokenize_and_stem(query)
    query_vec = vectorizer.transform([" ".join(query_tokens)])
    similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()

    ranked_indices = similarities.argsort()[::-1]
    ranked_results = [
        {
            "url": faculty_data[i]["url"],
            "snippet": faculty_data[i]["fac_main"][:200],
            "score": similarities[i],
        }
        for i in ranked_indices if similarities[i] > 0
    ]

    total_results = len(ranked_results)
    start_index = (page - 1) * results_per_page
    end_index = min(start_index + results_per_page, total_results)
    return ranked_results[start_index:end_index], total_results