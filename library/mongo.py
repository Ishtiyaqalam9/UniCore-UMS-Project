import os

from pymongo import ASCENDING, MongoClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DATABASE = os.getenv("MONGO_DATABASE", "library_db")

client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=1500,
    connectTimeoutMS=1500,
)
db = client[MONGO_DATABASE]
books = db["books"]
book_issues = db["book_issues"]


def ensure_indexes():
    """Create helpful indexes. MongoDB creates the database on first write."""
    books.create_index([("book_id", ASCENDING)], unique=True, sparse=True)
    books.create_index([("book_name", ASCENDING)])
    book_issues.create_index([("student_ref", ASCENDING)])
    book_issues.create_index([("borrower_ref", ASCENDING)])
    book_issues.create_index([("book_object_id", ASCENDING), ("status", ASCENDING)])


def is_available():
    try:
        client.admin.command("ping")
        return True
    except Exception:
        return False
