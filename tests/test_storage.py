
import pytest

from library_system.library import Library
from library_system.models import Book, Member
from library_system.storage import (
    StorageError,
    load_library,
    save_library,
)


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


def test_load_missing_file_raises_error(tmp_path):
    path = tmp_path / "missing.json"

    with pytest.raises(FileNotFoundError):
        load_library(path)


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

