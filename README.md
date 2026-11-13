# Library Management System

A small object-oriented library system in Python (standard library only).

## Features
- Books, members, borrow/return rules with a per-member limit
- Custom exceptions instead of printed errors
- CSV catalog import that reports bad rows instead of crashing
- Type hints throughout, checked with mypy; tests with pytest

## Run
    python -m venv .venv && source .venv/bin/activate
    pip install -r requirements-dev.txt
    python -m library_system

## Test
    pytest
    mypy library_system

## Structure
    library_system/   models, library, book_importer, storage, cli
    data/             books.csv (catalog)
    tests/            pytest suite


## Roadmap
- [x] Book, Member and Library classes
- [x] Custom exceptions
- [x] CSV catalog import with row validation
- [x] Tests (pytest) and type checking (mypy)
- [ ] JSON save/load
- [ ] Interactive menu (CLI)
- [ ] Overdue tracking and fines
- [x] Search by title
