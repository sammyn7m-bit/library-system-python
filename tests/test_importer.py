from pathlib import Path

from library_system.book_importer import import_books
from library_system.library import Library

DATA = Path(__file__).resolve().parent.parent / "data"


def test_clean_import() -> None:
    lib = Library()
    added, problems = import_books(lib, DATA / "books.csv")
    assert added == 3
    assert problems == []


def test_messy_import_reports_bad_rows() -> None:
    lib = Library()
    added, problems = import_books(lib, DATA / "books_messy.csv", replace=True)
    assert added == 2
    assert len(problems) == 3


def test_missing_file() -> None:
    added, problems = import_books(Library(), DATA / "nope.csv")
    assert added == 0
    assert "not found" in problems[0]
