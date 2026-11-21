from datetime import date

from library_system.models import Book

from pathlib import Path

import pytest

from library_system import cli
from library_system.library import Library
from library_system.models import Member
from library_system.storage import load_library


def test_start_imports_and_saves(tmp_path: Path) -> None:
    catalog = tmp_path / "books.csv"
    catalog.write_text("title,isbn\nA,1\nB,2\n", encoding="utf-8")
    state = tmp_path / "state.json"

    lib = cli.start_library(state, catalog)

    assert set(lib.books) == {"1", "2"}
    assert set(load_library(state).books) == {"1", "2"}


def test_restart_keeps_borrowed_state(tmp_path: Path) -> None:
    catalog = tmp_path / "books.csv"
    catalog.write_text("title,isbn\nA,1\n", encoding="utf-8")
    state = tmp_path / "state.json"

    lib = cli.start_library(state, catalog)
    lib.add_member(Member("sam", "M1"))
    lib.borrow_book("M1", "1")
    from library_system.storage import save_library
    save_library(lib, state)

    again = cli.start_library(state, catalog)
    assert not again.books["1"].is_available


# test search
def test_handle_search(monkeypatch: pytest.MonkeyPatch,
                       capsys: pytest.CaptureFixture[str]) -> None:
    lib = Library()
    from library_system.models import Book
    lib.add_book(Book("Clean Code", "222"))
    monkeypatch.setattr("builtins.input", lambda _: "clean")

    cli.handle_search(lib)

    assert "Clean Code" in capsys.readouterr().out

def test_handle_overdue_lists_late_loans(
    capsys: pytest.CaptureFixture[str],
) -> None:
    lib = Library()
    lib.add_book(Book("Clean Code", "222"))
    lib.add_member(Member("sam", "M1"))
    lib.borrow_book("M1", "222", today=date(2026, 1, 1))  # due 2026-01-15

    cli.handle_overdue(lib, today=date(2026, 1, 18))

    out = capsys.readouterr().out
    assert "Clean Code" in out
    assert "3 days late" in out
    assert "1.50" in out

# test overdue
def test_handle_overdue_when_none(capsys: pytest.CaptureFixture[str]) -> None:
    cli.handle_overdue(Library(), today=date(2026, 1, 1))
    assert "No overdue books." in capsys.readouterr().out
