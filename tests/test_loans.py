from datetime import date

from library_system.loans import Loan, days_late, fine_for, format_money

START = date(2026, 1, 1)


# create loan
def make_loan() -> Loan:
    return Loan.start("111", "M1", START)  # due 2026-01-15


# check due date
def test_due_date_is_14_days_out() -> None:
    assert make_loan().due_on == date(2026, 1, 15)


def test_no_fine_on_due_date() -> None:
    assert fine_for(make_loan(), date(2026, 1, 15)) == 0

# fine per day
def test_fine_per_day_late() -> None:
    assert days_late(make_loan(), date(2026, 1, 18)) == 3
    assert fine_for(make_loan(), date(2026, 1, 18)) == 150


def test_returned_loan_stops_accruing() -> None:
    loan = make_loan()
    loan.returned_on = date(2026, 1, 16)
    assert fine_for(loan, date(2026, 6, 1)) == 50


def test_fine_is_capped() -> None:
    assert fine_for(make_loan(), date(2027, 1, 1)) == 2000


def test_format_money() -> None:
    assert format_money(150) == "1.50"
    assert format_money(5) == "0.05"
    assert format_money(0) == "0.00"
