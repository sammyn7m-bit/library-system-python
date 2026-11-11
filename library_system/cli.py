from pathlib import Path

from .book_importer import import_books
from .library import Library

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def main() -> None:
    lib = Library()
    added, problems = import_books(lib, DATA_DIR / "books.csv")
    print(f"Imported {added} books")
    for problem in problems:
        print(f"Skipped: {problem}")

    for book in lib.available_books():
        print(book)


if __name__ == "__main__":
    main()
