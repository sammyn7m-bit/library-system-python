import pytest

from library_system.library import Library
from library_system.models import (
    Book,
    Member,
    BookUnavailableError,
    BorrowLimitError,
    DuplicateBookError,
    MemberNotFoundError,
    NotBorrowedError,
)


@pytest.fixture
def lib() -> Library:
    library = Library()
    library.add_book(Book("A", "1"))
    library.add_book(Book("B", "2"))
    library.add_member(Member("sam", "M1"))
    return library


def test_borrow_marks_book_unavailable(lib: Library) -> None:
    lib.borrow_book("M1", "1")
    assert not lib.books["1"].is_available
    assert len(lib.members["M1"].borrowed_books) == 1


def test_cannot_borrow_twice(lib: Library) -> None:
    lib.borrow_book("M1", "1")
    with pytest.raises(BookUnavailableError):
        lib.borrow_book("M1", "1")


def test_unknown_member(lib: Library) -> None:
    with pytest.raises(MemberNotFoundError):
        lib.borrow_book("X", "1")


def test_duplicate_book(lib: Library) -> None:
    with pytest.raises(DuplicateBookError):
        lib.add_book(Book("A again", "1"))


def test_borrow_limit(lib: Library) -> None:
    for isbn in ["3", "4", "5"]:
        lib.add_book(Book(isbn, isbn))
        lib.borrow_book("M1", isbn)
    with pytest.raises(BorrowLimitError):
        lib.borrow_book("M1", "1")


def test_return_restores_availability(lib: Library) -> None:
    lib.borrow_book("M1", "1")
    lib.return_book("M1", "1")
    assert lib.books["1"].is_available


def test_return_not_borrowed(lib: Library) -> None:
    with pytest.raises(NotBorrowedError):
        lib.return_book("M1", "1")
