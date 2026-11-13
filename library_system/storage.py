
"""JSON persistence for the library."""

import json
from pathlib import Path
from typing import Any

from .library import Library
from .models import Book, Member

DEFAULT_STORAGE_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "library.json"
)


class StorageError(Exception):
    """Raised when library data cannot be loaded or validated."""


def save_library(
    library: Library,
    path: Path = DEFAULT_STORAGE_PATH,
) -> None:
    """Save books and members to a JSON file."""

    books = []

    for book in library.books.values():
        books.append({
            "title": book.title,
            "isbn": book.isbn,
            "is_available": book.is_available,
        })

    members = []

    for member in library.members.values():
        borrowed_isbns = [
            book.isbn for book in member.borrowed_books
        ]

        members.append({
            "name": member.name,
            "member_id": member.member_id,
            "borrowed_isbns": borrowed_isbns,
        })

    data = {
        "version": 1,
        "books": books,
        "members": members,
    }

    path.parent.mkdir(parents=True, exist_ok=True)

    temporary_path = path.with_suffix(path.suffix + ".tmp")

    try:
        with temporary_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        temporary_path.replace(path)

    except OSError:
        if temporary_path.exists():
            temporary_path.unlink()
        raise


def load_library(
    path: Path = DEFAULT_STORAGE_PATH,
) -> Library:
    """Load library data and rebuild its Book and Member objects."""

    try:
        with path.open("r", encoding="utf-8") as file:
            data: Any = json.load(file)

    except FileNotFoundError:
        raise

    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise StorageError(
            f"Could not read valid JSON from {path}."
        ) from error

    if not isinstance(data, dict):
        raise StorageError("Library data must be a JSON object.")

    if data.get("version") != 1:
        raise StorageError("Unsupported or missing storage version.")

    books_data = data.get("books")
    members_data = data.get("members")

    if not isinstance(books_data, list):
        raise StorageError("'books' must be a list.")

    if not isinstance(members_data, list):
        raise StorageError("'members' must be a list.")

    library = Library()

    # Rebuild books first.
    for item in books_data:
        if not isinstance(item, dict):
            raise StorageError("Invalid book record.")

        title = item.get("title")
        isbn = item.get("isbn")
        is_available = item.get("is_available")

        if (
            not isinstance(title, str)
            or not isinstance(isbn, str)
            or not isinstance(is_available, bool)
        ):
            raise StorageError("Invalid book fields.")

        if isbn in library.books:
            raise StorageError(f"Duplicate ISBN: {isbn}")

        book = Book(title, isbn)
        book.is_available = is_available

        library.books[isbn] = book

    # Rebuild members and link borrowed books.
    borrowed_by: dict[str, str] = {}

    for item in members_data:
        if not isinstance(item, dict):
            raise StorageError("Invalid member record.")

        name = item.get("name")
        member_id = item.get("member_id")
        borrowed_isbns = item.get("borrowed_isbns")

        if (
            not isinstance(name, str)
            or not isinstance(member_id, str)
            or not isinstance(borrowed_isbns, list)
        ):
            raise StorageError("Invalid member fields.")

        if member_id in library.members:
            raise StorageError(f"Duplicate member ID: {member_id}")

        member = Member(name, member_id)

        for isbn in borrowed_isbns:
            if not isinstance(isbn, str):
                raise StorageError("Borrowed ISBNs must be strings.")

            book = library.books.get(isbn)

            if book is None:
                raise StorageError(
                    f"Member {member_id} references "
                    f"unknown book ISBN {isbn}."
                )

            if isbn in borrowed_by:
                raise StorageError(
                    f"Book {isbn} is assigned to multiple members."
                )

            borrowed_by[isbn] = member_id
            member.borrowed_books.append(book)

        library.members[member_id] = member

    # Check that availability agrees with borrowing records.
    for isbn, book in library.books.items():
        should_be_available = isbn not in borrowed_by

        if book.is_available != should_be_available:
            raise StorageError(
                f"Inconsistent availability for book {isbn}."
            )

    return library

