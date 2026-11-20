from pathlib import Path

from library_system.book_importer import import_books
from library_system.library import Library


# test csv write
def write_csv(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "books.csv"
    path.write_text(text, encoding="utf-8")
    return path


# chexk clean rows
def test_clean_rows(tmp_path: Path) -> None:
    path = write_csv(tmp_path, "title,isbn\nA,1\nB,2\n")
    added, problems = import_books(Library(), path)
    assert added == 2
    assert problems == []


# import of bad rows
def test_bad_rows_are_reported_with_line_numbers(tmp_path: Path) -> None:
    path = write_csv(
        tmp_path,
        "title,isbn\n"
        "A,1\n"
        "\n"
        "title,isbn\n"
        "No Isbn,\n"
        ",3\n"
        "A again,1\n",
    )
    added, problems = import_books(Library(), path)
    assert added == 1
    assert len(problems) == 3
    assert problems[0].startswith("line 5")
    assert problems[1].startswith("line 6")
    assert problems[2].startswith("line 7")


def test_replace_swaps_the_catalog(tmp_path: Path) -> None:
    lib = Library()
    import_books(lib, write_csv(tmp_path, "title,isbn\nOld,1\n"))
    import_books(lib, write_csv(tmp_path, "title,isbn\nNew,2\n"), replace=True)
    assert set(lib.books) == {"2"}


# missing file
def test_missing_file(tmp_path: Path) -> None:
    added, problems = import_books(Library(), tmp_path / "nope.csv")
    assert added == 0
    assert "not found" in problems[0]

# author column
def test_author_column_is_optional(tmp_path: Path) -> None:
    with_author = write_csv(tmp_path, "title,isbn,author\nA,1,Ann\n")
    lib = Library()
    import_books(lib, with_author)
    assert lib.books["1"].author == "Ann"

    without = tmp_path / "plain.csv"
    without.write_text("title,isbn\nB,2\n", encoding="utf-8")
    import_books(lib, without)
    assert lib.books["2"].author == ""
