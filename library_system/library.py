from .models import (
    Book,
    BookNotFoundError,
    BookUnavailableError,
    BorrowLimitError,
    DuplicateBookError,
    Member,
    MemberNotFoundError,
    NotBorrowedError,
)


class Library:
    def __init__(self) -> None:
        self.books: dict[str, Book] = {}
        self.members: dict[str, Member] = {}

    # add book to the library
    def add_book(self, book: Book) -> None:
        if book.isbn in self.books:
            raise DuplicateBookError(f"Book with ISBN {book.isbn} already exists.")
        self.books[book.isbn] = book

    # add a member
    def add_member(self, member: Member) -> None:
        self.members[member.member_id] = member

    # fuction for borrowing a book
    def borrow_book(self, member_id: str, isbn: str) -> None:
        member = self.members.get(member_id)
        if member is None:
            raise MemberNotFoundError(f"Member {member_id} does not exist.")

        book = self.books.get(isbn)
        if book is None:
            raise BookNotFoundError(f"Book with ISBN {isbn} does not exist.")

        if not book.is_available:
            raise BookUnavailableError(f"'{book.title}' is currently borrowed.")

        if not member.can_borrow:
            raise BorrowLimitError(
                f"{member.name} hit the limit of {Member.MAX_BOOKS} books."
            )

        book.is_available = False
        member.borrowed_books.append(book)

    def return_book(self, member_id: str, isbn: str) -> None:
        member = self.members.get(member_id)
        if member is None:
            raise MemberNotFoundError(f"Member {member_id} does not exist.")

        book = self.books.get(isbn)
        if book is None:
            raise BookNotFoundError(f"Book with ISBN {isbn} does not exist.")

        if book not in member.borrowed_books:
            raise NotBorrowedError(f"{member.name} has not borrowed '{book.title}'.")

        member.borrowed_books.remove(book)
        book.is_available = True


    # check availability of a book
    def available_books(self) -> list[Book]:
        return [book for book in self.books.values() if book.is_available]

    # search for books in the library
    def search_books(self, query: str) -> list[Book]:
        """Return books whose title or ISBN contains the query (case-insensitive)."""
        query = query.strip().lower()
        if not query:
            return []
        return [
            book
            for book in self.books.values()
            if query in book.title.lower() or query in book.isbn.lower()
        ]
