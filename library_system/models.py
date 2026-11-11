class BookNotFoundError(Exception):
    """Raised when a book is not in the library."""


class BookUnavailableError(Exception):
    """Raised when a book is already borrowed."""


class BorrowLimitError(Exception):
    """Raised when a member has reached the borrow limit."""


class MemberNotFoundError(Exception):
    """Raised when a member id is not registered."""


class DuplicateBookError(Exception):
    """Raised when a book with the same ISBN already exists."""


class NotBorrowedError(Exception):
    """Raised when a member returns a book they did not borrow."""


class Book:
    def __init__(self, title: str, isbn: str) -> None:
        self.title: str = title
        self.isbn: str = isbn
        self.is_available: bool = True

    def __str__(self) -> str:
        status = "Available" if self.is_available else "Borrowed"
        return f"{self.title} ({self.isbn}) - {status}"

    def __repr__(self) -> str:
        return f"Book(title={self.title!r}, isbn={self.isbn!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Book):
            return NotImplemented
        return self.isbn == other.isbn

    def __hash__(self) -> int:
        return hash(self.isbn)


class Member:
    MAX_BOOKS: int = 3

    def __init__(self, name: str, member_id: str) -> None:
        self.name: str = name
        self.member_id: str = member_id
        self.borrowed_books: list[Book] = []

    @property
    def can_borrow(self) -> bool:
        return len(self.borrowed_books) < self.MAX_BOOKS

    def __str__(self) -> str:
        return f"{self.name} ({self.member_id}) - {len(self.borrowed_books)} borrowed"

    def __repr__(self) -> str:
        return f"Member(name={self.name!r}, member_id={self.member_id!r})"
