import csv
from pathlib import Path

from .library import Library
from .models import Book, DuplicateBookError


def import_books(
    library: Library, csv_path: Path, replace: bool = False
) -> tuple[int, list[str]]:
    """Add books from a CSV file. With replace=True, the file becomes the whole catalog."""
    problems: list[str] = []
    parsed: list[tuple[int, Book]] = []
    seen: set[str] = set()

    if replace and any(not b.is_available for b in library.books.values()):
        return 0, ["cannot replace the catalog while books are borrowed"]

    try:
        with open(csv_path, "r", newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            if reader.fieldnames is None:
                return 0, ["CSV is empty"]

            reader.fieldnames = [name.strip().lower() for name in reader.fieldnames]
            if not {"title", "isbn"} <= set(reader.fieldnames):
                return 0, ["CSV must have 'title' and 'isbn' columns"]

            for row in reader:
                line_no = reader.line_num
                title = (row.get("title") or "").strip()
                isbn = (row.get("isbn") or "").strip()

                if not title and not isbn:
                    continue
                if title.lower() == "title" and isbn.lower() == "isbn":
                    continue
                if not title or not isbn:
                    problems.append(f"line {line_no}: missing title or isbn")
                    continue
                if isbn in seen:
                    problems.append(f"line {line_no}: isbn {isbn} repeated in file")
                    continue

                seen.add(isbn)
                parsed.append((line_no, Book(title, isbn)))

    except FileNotFoundError:
        return 0, [f"{csv_path} not found"]
    except OSError as e:
        return 0, [f"could not read {csv_path}: {e}"]

    if replace:
        library.books.clear()

    added = 0
    for line_no, book in parsed:
        try:
            library.add_book(book)
            added += 1
        except DuplicateBookError:
            problems.append(f"line {line_no}: isbn {book.isbn} already exists")

    return added, problems
