"""JSON save/load for the library state. TODO: write this yourself.

Save: each book's title, isbn, is_available; each member's name, member_id,
and a list of borrowed ISBNs.
Load: rebuild Books first, then Members, linking borrowed ISBNs to the
shared Book objects.
"""
