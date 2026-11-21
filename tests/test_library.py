import pytest

from datetime import date
from library_system.library import Library
from library_system.models import (
    Book,
    BookUnavailableError,
    BorrowLimitError,
    DuplicateBookError,
    DuplicateMemberError,
    Member,
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


# test availabilitt of a book
def test_borrow_marks_book_unavailable(lib: Library) -> None:
    lib.borrow_book("M1", "1")
    assert not lib.books["1"].is_available
    assert len(lib.members["M1"].borrowed_books) == 1


# cannot borrow book twice
def test_cannot_borrow_twice(lib: Library) -> None:
    lib.borrow_book("M1", "1")
    with pytest.raises(BookUnavailableError):
        lib.borrow_book("M1", "1")


# test with an unknown member
def test_unknown_member(lib: Library) -> None:
    with pytest.raises(MemberNotFoundError):
        lib.borrow_book("X", "1")


def test_duplicate_member(lib: Library) -> None:
    with pytest.raises(DuplicateMemberError):
        lib.add_member(Member("sam again", "M1"))


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

# search by title
def test_search_by_title(lib: Library) -> None:
    assert lib.search_books("a") == [lib.books["1"]]


# search by isbn
def test_search_by_isbn(lib: Library) -> None:
    assert lib.search_books("2") == [lib.books["2"]]


# search by empty
def test_search_no_match_and_empty(lib: Library) -> None:
    assert lib.search_books("zzz") == []
    assert lib.search_books("   ") == []

# search by author
def test_search_by_author() -> None:
    library = Library()
    library.add_book(Book("Clean Code", "222", "Robert C. Martin"))
    assert library.search_books("martin") == [library.books["222"]]


def test_borrow_creates_loan(lib: Library) -> None:
    lib.borrow_book("M1", "1", today=date(2026, 1, 1))
    assert lib.loans[0].due_on == date(2026, 1, 15)


def test_return_on_time_has_no_fine(lib: Library) -> None:
    lib.borrow_book("M1", "1", today=date(2026, 1, 1))
    assert lib.return_book("M1", "1", today=date(2026, 1, 15)) == 0


def test_return_late_gives_fine(lib: Library) -> None:
    lib.borrow_book("M1", "1", today=date(2026, 1, 1))
    assert lib.return_book("M1", "1", today=date(2026, 1, 18)) == 150


def test_return_closes_loan(lib: Library) -> None:
    lib.borrow_book("M1", "1", today=date(2026, 1, 1))
    lib.return_book("M1", "1", today=date(2026, 1, 5))
    assert lib.loans[0].returned_on == date(2026, 1, 5)


def test_overdue_loans(lib: Library) -> None:
    lib.borrow_book("M1", "1", today=date(2026, 1, 1))
    assert lib.overdue_loans(date(2026, 1, 15)) == []
    assert len(lib.overdue_loans(date(2026, 1, 16))) == 1


def test_return_without_loan_record_has_no_fine(lib: Library) -> None:
    lib.borrow_book("M1", "1", today=date(2026, 1, 1))
    lib.loans.clear()  # as after loading a file saved before loans existed
    assert lib.return_book("M1", "1", today=date(2026, 3, 1)) == 0
