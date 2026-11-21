import json
from datetime import date

import pytest

from library_system.library import Library
from library_system.models import Book, Member
from library_system.storage import (
    StorageError,
    load_library,
    save_library,
)


# save/load library
def test_save_and_load_library(tmp_path):
    path = tmp_path / "library.json"

    library = Library()
    library.add_book(Book("Python Basics", "ISBN001"))
    library.add_book(Book("Django Guide", "ISBN002"))
    library.add_member(Member("Sam", "M001"))

    library.borrow_book("M001", "ISBN001")

    save_library(library, path)
    loaded = load_library(path)

    assert len(loaded.books) == 2
    assert len(loaded.members) == 1

    assert loaded.books["ISBN001"].is_available is False
    assert loaded.books["ISBN002"].is_available is True

    member = loaded.members["M001"]

    assert member.name == "Sam"
    assert len(member.borrowed_books) == 1
    assert member.borrowed_books[0].isbn == "ISBN001"

    # The borrowed book must be the same object
    # stored in the library's books dictionary.
    assert (
        member.borrowed_books[0]
        is loaded.books["ISBN001"]
    )


# missing file
def test_load_missing_file_raises_error(tmp_path):
    path = tmp_path / "missing.json"

    with pytest.raises(FileNotFoundError):
        load_library(path)


# 8nvalid json
def test_load_invalid_json_raises_storage_error(tmp_path):
    path = tmp_path / "library.json"
    path.write_text("{invalid json", encoding="utf-8")

    with pytest.raises(StorageError):
        load_library(path)


def test_empty_library_can_be_saved_and_loaded(tmp_path):
    path = tmp_path / "library.json"

    library = Library()

    save_library(library, path)
    loaded = load_library(path)

    assert loaded.books == {}
    assert loaded.members == {}

# test author
def test_author_round_trip(tmp_path: Path) -> None:
    library = Library()
    library.add_book(Book("A", "1", "Ann"))
    path = tmp_path / "lib.json"
    save_library(library, path)
    assert load_library(path).books["1"].author == "Ann"


# test loans
def test_loans_round_trip(tmp_path: Path) -> None:
    library = Library()
    library.add_book(Book("A", "1"))
    library.add_member(Member("sam", "M1"))
    library.borrow_book("M1", "1", today=date(2026, 1, 1))
    library.return_book("M1", "1", today=date(2026, 1, 20))
    library.borrow_book("M1", "1", today=date(2026, 2, 1))

    path = tmp_path / "lib.json"
    save_library(library, path)

    assert load_library(path).loans == library.loans


def test_version_1_file_is_migrated(tmp_path: Path) -> None:
    path = tmp_path / "old.json"
    path.write_text(json.dumps({
        "version": 1,
        "books": [{"title": "A", "isbn": "1", "is_available": False}],
        "members": [{"name": "sam", "member_id": "M1", "borrowed_isbns": ["1"]}],
    }))

    loaded = load_library(path)

    assert len(loaded.loans) == 1
    assert loaded.loans[0].isbn == "1"
    assert loaded.loans[0].returned_on is None


# test invalid date
def test_invalid_loan_date(lib: Library, tmp_path: Path) -> None:
    path = tmp_path / "lib.json"
    save_library(lib, path)
    data = json.loads(path.read_text())
    data["loans"][0]["due_on"] = "not-a-date"
    path.write_text(json.dumps(data))
    with pytest.raises(StorageError):
        load_library(path)


def test_open_loan_missing(lib: Library, tmp_path: Path) -> None:
    path = tmp_path / "lib.json"
    save_library(lib, path)
    data = json.loads(path.read_text())
    data["loans"] = []
    path.write_text(json.dumps(data))
    with pytest.raises(StorageError):
        load_library(path)


@pytest.fixture
def lib() -> Library:
    library = Library()
    library.add_book(Book("A", "1"))
    library.add_book(Book("B", "2"))
    library.add_member(Member("sam", "M1"))
    library.borrow_book("M1", "1", today=date(2026, 1, 1))
    return library
