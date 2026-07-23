import re
import logging
logger = logging.getLogger(__name__)
from datetime import datetime, timedelta, timezone

from bson import ObjectId
from bson.errors import InvalidId
from django.contrib import messages
from django.shortcuts import redirect, render
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError, PyMongoError

from accounts.decorators import role_required
from accounts.models import UserProfile
from accounts.utils import get_user_profile, get_user_role
from student.models import Student
from teacher.models import Teacher

from .forms import BookForm, IssueBookForm
from .mongo import book_issues, books, ensure_indexes, is_available


def _object_id(value):
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        return None


def _mongo_error(request, exc):
    logger.exception("MongoDB operation failed: %s", exc)

    messages.error(
        request,
        "The library service is currently unavailable. "
        "Please try again after the service is started."
    )


def _member_identity(request):
    profile = get_user_profile(request.user)
    role = get_user_role(request.user)
    borrower_type = "Student" if role == UserProfile.STUDENT else "Teacher"
    reference = profile.reference_id
    name = profile.display_name or request.user.username
    try:
        if role == UserProfile.STUDENT:
            person = Student.objects.filter(student_id=reference).first()
        else:
            person = Teacher.objects.filter(employee_id=reference).first()
        if person:
            name = person.name
    except Exception:
        pass
    return borrower_type, reference, name


def _member_query(reference):
    return {"$or": [{"borrower_ref": reference}, {"student_ref": reference}]}


def library_list(request):
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()
    mongo_online = is_available()
    all_books = []
    categories = []

    if mongo_online:
        try:
            ensure_indexes()
            filters = {}
            if query:
                safe = re.escape(query)
                filters["$or"] = [
                    {"book_id": {"$regex": safe, "$options": "i"}},
                    {"book_name": {"$regex": safe, "$options": "i"}},
                    {"writer": {"$regex": safe, "$options": "i"}},
                    {"isbn": {"$regex": safe, "$options": "i"}},
                ]
            if category:
                filters["category"] = category

            for book in books.find(filters).sort("book_name", 1):
                total = int(book.get("total_copies", 1) or 1)
                available = int(book.get("available_copies", total) if book.get("available_copies") is not None else total)
                book["id"] = str(book["_id"])
                book["total_copies"] = total
                book["available_copies"] = available
                all_books.append(book)
            categories = [item for item in books.distinct("category") if item]
        except PyMongoError as exc:
            _mongo_error(request, exc)
            mongo_online = False

    return render(
        request,
        "library/library_list.html",
        {
            "books": all_books,
            "categories": sorted(categories),
            "query": query,
            "selected_category": category,
            "mongo_online": mongo_online,
            "member_mode": False,
        },
    )


@role_required(UserProfile.STUDENT, UserProfile.TEACHER)
def member_library_catalog(request):
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()
    mongo_online = is_available()
    all_books = []
    categories = []
    active_book_ids = set()
    borrower_type, reference, name = _member_identity(request)

    if mongo_online:
        try:
            ensure_indexes()
            filters = {}
            if query:
                safe = re.escape(query)
                filters["$or"] = [
                    {"book_id": {"$regex": safe, "$options": "i"}},
                    {"book_name": {"$regex": safe, "$options": "i"}},
                    {"writer": {"$regex": safe, "$options": "i"}},
                    {"isbn": {"$regex": safe, "$options": "i"}},
                ]
            if category:
                filters["category"] = category
            active_book_ids = {
                item.get("book_object_id")
                for item in book_issues.find({"$and": [_member_query(reference), {"status": "Issued"}]}, {"book_object_id": 1})
            }
            for book in books.find(filters).sort("book_name", 1):
                total = int(book.get("total_copies", 1) or 1)
                available = int(book.get("available_copies", total) if book.get("available_copies") is not None else total)
                book["id"] = str(book["_id"])
                book["total_copies"] = total
                book["available_copies"] = available
                book["already_issued"] = book["id"] in active_book_ids
                all_books.append(book)
            categories = [item for item in books.distinct("category") if item]
        except PyMongoError as exc:
            _mongo_error(request, exc)
            mongo_online = False

    return render(
        request,
        "library/member_catalog.html",
        {
            "books": all_books,
            "categories": sorted(categories),
            "query": query,
            "selected_category": category,
            "mongo_online": mongo_online,
            "borrower_type": borrower_type,
            "borrower_name": name,
        },
    )


def add_book(request):
    form = BookForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        try:
            ensure_indexes()
            books.insert_one(
                {
                    "book_id": data["book_id"],
                    "book_name": data["book_name"],
                    "writer": data["writer"],
                    "isbn": data["isbn"],
                    "category": data["category"],
                    "total_copies": data["total_copies"],
                    "available_copies": data["total_copies"],
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc),
                }
            )
            messages.success(request, "Book added successfully.")
            return redirect("library_list")
        except DuplicateKeyError:
            form.add_error("book_id", "This Book ID already exists.")
        except PyMongoError as exc:
            _mongo_error(request, exc)
    return render(request, "library/book_form.html", {"form": form, "title": "Add Book"})


def edit_book(request, id):
    object_id = _object_id(id)
    if object_id is None:
        messages.error(request, "Invalid book identifier.")
        return redirect("library_list")
    try:
        book = books.find_one({"_id": object_id})
    except PyMongoError as exc:
        _mongo_error(request, exc)
        return redirect("library_list")
    if not book:
        messages.error(request, "Book not found.")
        return redirect("library_list")

    initial = {
        "book_id": book.get("book_id", ""),
        "book_name": book.get("book_name", ""),
        "writer": book.get("writer", ""),
        "isbn": book.get("isbn", ""),
        "category": book.get("category", ""),
        "total_copies": book.get("total_copies", 1),
    }
    form = BookForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        old_total = int(book.get("total_copies", 1) or 1)
        old_available = int(book.get("available_copies", old_total) if book.get("available_copies") is not None else old_total)
        issued_count = max(old_total - old_available, 0)
        if data["total_copies"] < issued_count:
            form.add_error("total_copies", f"At least {issued_count} copies are currently issued.")
        else:
            try:
                books.update_one(
                    {"_id": object_id},
                    {
                        "$set": {
                            "book_id": data["book_id"],
                            "book_name": data["book_name"],
                            "writer": data["writer"],
                            "isbn": data["isbn"],
                            "category": data["category"],
                            "total_copies": data["total_copies"],
                            "available_copies": data["total_copies"] - issued_count,
                            "updated_at": datetime.now(timezone.utc),
                        }
                    },
                )
                messages.success(request, "Book updated successfully.")
                return redirect("library_list")
            except DuplicateKeyError:
                form.add_error("book_id", "This Book ID already exists.")
            except PyMongoError as exc:
                _mongo_error(request, exc)
    return render(request, "library/book_form.html", {"form": form, "title": "Edit Book", "book": book})


def delete_book(request, id):
    object_id = _object_id(id)
    if object_id is None:
        messages.error(request, "Invalid book identifier.")
        return redirect("library_list")
    try:
        book = books.find_one({"_id": object_id})
        if not book:
            messages.error(request, "Book not found.")
            return redirect("library_list")
        if request.method == "POST":
            active = book_issues.count_documents({"book_object_id": str(object_id), "status": "Issued"})
            if active:
                messages.error(request, "This book cannot be deleted while copies are issued.")
                return redirect("library_list")
            books.delete_one({"_id": object_id})
            messages.success(request, "Book deleted successfully.")
            return redirect("library_list")
        return render(request, "library/book_confirm_delete.html", {"book": book})
    except PyMongoError as exc:
        _mongo_error(request, exc)
        return redirect("library_list")


def _create_issue(*, object_id, book, borrower_type, borrower_ref, borrower_name, due_date, notes=""):
    total_copies = int(book.get("total_copies", 1) or 1)
    books.update_one(
        {"_id": object_id, "available_copies": {"$exists": False}},
        {"$set": {"total_copies": total_copies, "available_copies": total_copies}},
    )
    updated = books.find_one_and_update(
        {"_id": object_id, "available_copies": {"$gt": 0}},
        {"$inc": {"available_copies": -1}, "$set": {"updated_at": datetime.now(timezone.utc)}},
        return_document=ReturnDocument.AFTER,
    )
    if not updated:
        return False
    try:
        document = {
            "book_object_id": str(object_id),
            "book_id": book.get("book_id", ""),
            "book_name": book.get("book_name", ""),
            "borrower_type": borrower_type,
            "borrower_ref": borrower_ref,
            "borrower_name": borrower_name,
            "issue_date": datetime.now(timezone.utc),
            "due_date": datetime.combine(due_date, datetime.min.time(), tzinfo=timezone.utc),
            "returned_at": None,
            "status": "Issued",
            "notes": notes,
        }
        if borrower_type == "Student":
            document["student_ref"] = borrower_ref
            document["student_name"] = borrower_name
        book_issues.insert_one(document)
    except Exception:
        books.update_one({"_id": object_id}, {"$inc": {"available_copies": 1}})
        raise
    return True


def issue_book(request, id):
    object_id = _object_id(id)
    if object_id is None:
        messages.error(request, "Invalid book identifier.")
        return redirect("library_list")
    try:
        book = books.find_one({"_id": object_id})
    except PyMongoError as exc:
        _mongo_error(request, exc)
        return redirect("library_list")
    if not book:
        messages.error(request, "Book not found.")
        return redirect("library_list")

    form = IssueBookForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        try:
            duplicate = book_issues.count_documents(
                {
                    "book_object_id": str(object_id),
                    "borrower_ref": data["borrower_ref"],
                    "status": "Issued",
                }
            )
            if duplicate:
                messages.warning(request, "This borrower already has an active copy of this book.")
                return redirect("issue_list")
            created = _create_issue(
                object_id=object_id,
                book=book,
                borrower_type=data["borrower_type"],
                borrower_ref=data["borrower_ref"],
                borrower_name=data["borrower_name"],
                due_date=data["due_date"],
                notes=data["notes"],
            )
            if not created:
                messages.error(request, "No copy is currently available for issue.")
                return redirect("library_list")
            messages.success(request, f"{book.get('book_name', 'Book')} issued successfully.")
            return redirect("issue_list")
        except PyMongoError as exc:
            _mongo_error(request, exc)
    book["id"] = str(book["_id"])
    return render(request, "library/issue_book.html", {"form": form, "book": book})


@role_required(UserProfile.STUDENT, UserProfile.TEACHER)
def self_issue_book(request, id):
    object_id = _object_id(id)
    if object_id is None:
        messages.error(request, "Invalid book identifier.")
        return redirect("member_library_catalog")
    borrower_type, reference, name = _member_identity(request)
    try:
        book = books.find_one({"_id": object_id})
        if not book:
            messages.error(request, "Book not found.")
            return redirect("member_library_catalog")
        book["id"] = str(book["_id"])
        active_count = book_issues.count_documents({"$and": [_member_query(reference), {"status": "Issued"}]})
        duplicate = book_issues.count_documents(
            {"book_object_id": str(object_id), "borrower_ref": reference, "status": "Issued"}
        )
        if request.method == "POST":
            if duplicate:
                messages.warning(request, "You already have this book issued.")
                return redirect("my_library")
            if active_count >= 5:
                messages.error(request, "You can keep a maximum of five active library books.")
                return redirect("my_library")
            due_date = (datetime.now(timezone.utc) + timedelta(days=14)).date()
            created = _create_issue(
                object_id=object_id,
                book=book,
                borrower_type=borrower_type,
                borrower_ref=reference,
                borrower_name=name,
                due_date=due_date,
            )
            if not created:
                messages.error(request, "No copy is currently available.")
                return redirect("member_library_catalog")
            messages.success(request, f"{book.get('book_name')} has been issued to your account for 14 days.")
            return redirect("my_library")
        return render(
            request,
            "library/member_issue_confirm.html",
            {
                "book": book,
                "borrower_type": borrower_type,
                "borrower_ref": reference,
                "borrower_name": name,
                "due_date": datetime.now(timezone.utc).date() + timedelta(days=14),
                "duplicate": bool(duplicate),
                "active_count": active_count,
            },
        )
    except PyMongoError as exc:
        _mongo_error(request, exc)
        return redirect("member_library_catalog")


def issue_list(request):
    status = request.GET.get("status", "Issued").strip()
    query = request.GET.get("q", "").strip()
    records = []
    try:
        filters = {}
        if status:
            filters["status"] = status
        if query:
            safe = re.escape(query)
            filters["$or"] = [
                {"borrower_ref": {"$regex": safe, "$options": "i"}},
                {"borrower_name": {"$regex": safe, "$options": "i"}},
                {"student_ref": {"$regex": safe, "$options": "i"}},
                {"student_name": {"$regex": safe, "$options": "i"}},
                {"book_id": {"$regex": safe, "$options": "i"}},
                {"book_name": {"$regex": safe, "$options": "i"}},
            ]
        for record in book_issues.find(filters).sort("issue_date", -1):
            record["id"] = str(record["_id"])
            record["display_ref"] = record.get("borrower_ref") or record.get("student_ref", "")
            record["display_name"] = record.get("borrower_name") or record.get("student_name", "")
            record["display_type"] = record.get("borrower_type") or "Student"
            records.append(record)
    except PyMongoError as exc:
        _mongo_error(request, exc)
    return render(
        request,
        "library/issue_list.html",
        {"records": records, "selected_status": status, "query": query},
    )


@role_required(UserProfile.STUDENT, UserProfile.TEACHER)
def my_library(request):
    borrower_type, reference, name = _member_identity(request)
    status = request.GET.get("status", "").strip()
    records = []
    mongo_online = is_available()
    if mongo_online:
        try:
            filters = _member_query(reference)
            if status:
                filters = {"$and": [filters, {"status": status}]}
            for record in book_issues.find(filters).sort("issue_date", -1):
                record["id"] = str(record["_id"])
                records.append(record)
        except PyMongoError as exc:
            _mongo_error(request, exc)
            mongo_online = False
    return render(
        request,
        "library/my_library.html",
        {
            "records": records,
            "selected_status": status,
            "mongo_online": mongo_online,
            "borrower_type": borrower_type,
            "borrower_name": name,
        },
    )


def return_book(request, id):
    if request.method != "POST":
        return redirect("issue_list")
    issue_id = _object_id(id)
    if issue_id is None:
        messages.error(request, "Invalid issue identifier.")
        return redirect("issue_list")
    try:
        issue = book_issues.find_one_and_update(
            {"_id": issue_id, "status": "Issued"},
            {"$set": {"status": "Returned", "returned_at": datetime.now(timezone.utc)}},
            return_document=ReturnDocument.BEFORE,
        )
        if not issue:
            messages.warning(request, "This issue record was already returned or does not exist.")
            return redirect("issue_list")
        book_object_id = _object_id(issue.get("book_object_id"))
        if book_object_id:
            books.update_one({"_id": book_object_id}, {"$inc": {"available_copies": 1}})
        messages.success(request, "Book returned successfully.")
    except PyMongoError as exc:
        _mongo_error(request, exc)
    return redirect("issue_list")


@role_required(UserProfile.STUDENT, UserProfile.TEACHER)
def member_return_book(request, id):
    if request.method != "POST":
        return redirect("my_library")
    issue_id = _object_id(id)
    if issue_id is None:
        messages.error(request, "Invalid issue identifier.")
        return redirect("my_library")
    _, reference, _ = _member_identity(request)
    try:
        issue = book_issues.find_one_and_update(
            {"_id": issue_id, "status": "Issued", "$or": [{"borrower_ref": reference}, {"student_ref": reference}]},
            {"$set": {"status": "Returned", "returned_at": datetime.now(timezone.utc)}},
            return_document=ReturnDocument.BEFORE,
        )
        if not issue:
            messages.warning(request, "This book is already returned or does not belong to your account.")
            return redirect("my_library")
        book_object_id = _object_id(issue.get("book_object_id"))
        if book_object_id:
            books.update_one({"_id": book_object_id}, {"$inc": {"available_copies": 1}})
        messages.success(request, "Book returned successfully.")
    except PyMongoError as exc:
        _mongo_error(request, exc)
    return redirect("my_library")
