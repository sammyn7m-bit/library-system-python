from pathlib import Path
from .loans import format_money
from .book_importer import import_books
from .library import Library
from .models import LibraryError, Member
from .storage import DEFAULT_STORAGE_PATH, StorageError, load_library, save_library

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CATALOG_PATH = DATA_DIR / "books.csv"

MENU = """
1. Borrow a book
2. Return a book
3. Search books
4. List available books
5. Add member
6. Quit"""


def start_library(
    state_path: Path = DEFAULT_STORAGE_PATH,
    catalog_path: Path = CATALOG_PATH,
) -> Library:
    """Load saved state (or start empty), then import new catalog books."""
    try:
        lib = load_library(state_path)
    except FileNotFoundError:
        lib = Library()

    added, problems = import_books(lib, catalog_path)
    # books already in the saved state are expected duplicates, not problems
    problems = [p for p in problems if "already exists" not in p]

    if added:
        print(f"Imported {added} new books")
        save_library(lib, state_path)
    for problem in problems:
        print(f"Skipped: {problem}")
    return lib


def ask(prompt: str) -> str:
    return input(prompt).strip()


# hamdle book borrowing
def handle_borrow(lib: Library) -> None:
    member_id = ask("Member ID: ")
    isbn = ask("Book ISBN: ")
    lib.borrow_book(member_id, isbn)
    save_library(lib)
    print(f"Borrowed: {lib.books[isbn].title}")


# handle books found
def handle_return(lib: Library) -> None:
    member_id = ask("Member ID: ")
    isbn = ask("Book ISBN: ")
    fine = lib.return_book(member_id, isbn)
    save_library(lib)
    print(f"Returned: {lib.books[isbn].title}")
    if fine:
        print(f"Late fee: {format_money(fine)}")

# searxh results
def handle_search(lib: Library) -> None:
    results = lib.search_books(ask("Search by title, author or ISBN: "))
    if not results:
        print("No books found.")
    for book in results:
        print(book)


# check if book is available
def handle_list_available(lib: Library) -> None:
    books = lib.available_books()
    if not books:
        print("No books available.")
    for book in books:
        print(book)


# add member
def handle_add_member(lib: Library) -> None:
    name = ask("Member name: ")
    member_id = ask("Member ID: ")
    if not name or not member_id:
        print("Name and ID cannot be empty.")
        return
    lib.add_member(Member(name, member_id))
    save_library(lib)
    print(f"Added member {name} ({member_id})")


def main() -> None:
    try:
        lib = start_library()
    except StorageError as e:
        raise SystemExit(f"Cannot start: {e}")

    handlers = {
        "1": handle_borrow,
        "2": handle_return,
        "3": handle_search,
        "4": handle_list_available,
        "5": handle_add_member,
    }

    while True:
        print(MENU)
        choice = ask("Choose: ")
        if choice == "6":
            break
        handler = handlers.get(choice)
        if handler is None:
            print("Invalid choice.")
            continue
        try:
            handler(lib)
        except LibraryError as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
