
from pathlib import Path

from .book_importer import import_books
from .library import Library
from .storage import (
    DEFAULT_STORAGE_PATH,
    load_library,
    save_library,
)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def main() -> None:
    if DEFAULT_STORAGE_PATH.exists():
        lib = load_library()
        print("Loaded saved library data.")

    else:
        lib = Library()

        added, problems = import_books(
            lib,
            DATA_DIR / "books.csv",
        )

        print(f"Imported {added} books from CSV.")

        for problem in problems:
            print(f"Skipped: {problem}")

        save_library(lib)
        print("Library data saved.")

    print("\nAvailable books:")

    for book in lib.available_books():
        print(book)


if __name__ == "__main__":
    main()

