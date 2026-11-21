from dataclasses import dataclass
from datetime import date, timedelta

LOAN_DAYS = 14
FINE_PER_DAY_CENTS = 50
MAX_FINE_CENTS = 2000


@dataclass
class Loan:
    isbn: str
    member_id: str
    borrowed_on: date
    due_on: date
    returned_on: date | None = None

    @classmethod
    def start(cls, isbn: str, member_id: str, borrowed_on: date) -> "Loan":
        return cls(isbn, member_id, borrowed_on, borrowed_on + timedelta(days=LOAN_DAYS))

    @property
    def is_returned(self) -> bool:
        return self.returned_on is not None


def days_late(loan: Loan, today: date) -> int:
    """Whole days past the due date. Uses the return date if returned."""
    end = loan.returned_on or today
    return max(0, (end - loan.due_on).days)


def fine_for(loan: Loan, today: date) -> int:
    """Fine in cents, capped at MAX_FINE_CENTS."""
    return min(days_late(loan, today) * FINE_PER_DAY_CENTS, MAX_FINE_CENTS)


def format_money(cents: int) -> str:
    return f"{cents // 100}.{cents % 100:02d}"
