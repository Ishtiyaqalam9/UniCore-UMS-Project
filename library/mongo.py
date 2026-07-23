import logging
import os

from pymongo import ASCENDING, MongoClient

logger = logging.getLogger(__name__)

# Supports both local MONGO_URI and Railway MONGO_URL.
MONGO_URI = (
    os.getenv("MONGO_URI")
    or os.getenv("MONGO_URL")
    or "mongodb://localhost:27017/"
).strip()

MONGO_DATABASE = os.getenv("MONGO_DATABASE", "library_db").strip()

client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=10000,
    connectTimeoutMS=10000,
    socketTimeoutMS=10000,
    appname="UniCore-UMS",
)

db = client[MONGO_DATABASE]
books = db["books"]
book_issues = db["book_issues"]


def ensure_indexes():
    """Create useful indexes. MongoDB creates the database on first write."""
    books.create_index(
        [("book_id", ASCENDING)],
        unique=True,
        sparse=True,
    )
    books.create_index([("book_name", ASCENDING)])
    book_issues.create_index([("student_ref", ASCENDING)])
    book_issues.create_index([("borrower_ref", ASCENDING)])
    book_issues.create_index(
        [("book_object_id", ASCENDING), ("status", ASCENDING)]
    )


def is_available():
    try:
        client.admin.command("ping")
        return True
    except Exception as exc:
        logger.exception("MongoDB connection failed: %s", exc)
        return False
