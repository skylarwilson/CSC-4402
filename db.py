"""SQLite Database.

This module encapsulates DB access: connection management, schema creation,
and CRUD helpers.
"""

import os
import sqlite3
from typing import Iterable, Optional
from .gen_data import (
    generate_cards,
    generate_employees
)


# Default DB lives alongside the package (created on demand).
DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shop.db")


SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    set_name TEXT NOT NULL,
    rarity TEXT NOT NULL,
    price_cents INTEGER NOT NULL CHECK(price_cents >= 0),
    stock INTEGER NOT NULL DEFAULT 0 CHECK(stock >= 0)
);

CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    city TEXT NOT NULL
);
"""


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Open a connection with row_factory set to ``sqlite3.Row``.

    Ensures the parent directory for the DB file exists so first-time usage
    works without needing to create folders manually.
    """
    path = db_path or DEFAULT_DB_PATH
    dirpath = os.path.dirname(path)
    if dirpath:
        os.makedirs(dirpath, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Optional[str] = None) -> None:
    """Create tables if missing and seeds sample data."""

    with get_connection(db_path) as conn:
        conn.executescript(SCHEMA_SQL)

        card_count = conn.execute("SELECT COUNT(*) FROM cards").fetchone()[0]
        if card_count == 0:
            cards = generate_cards(count=25)
            conn.executemany(
                "INSERT INTO cards(name, set_name, rarity, price_cents, stock) VALUES (?,?,?,?,?)",
                cards,
            )

        employee_count = conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
        if employee_count == 0:
            employees = generate_employees(count=4)
            conn.executemany(
                "INSERT INTO employees(first_name, last_name, city) VALUES (?,?,?)",
                employees,
            )

def add_emp(
    first_name: str,
    last_name: str,
    city: str,
    db_path: Optional[str] = None,
) -> int:
    """Insert a new employee and return the new row id."""

    with get_connection(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO employees(first_name, last_name, city) VALUES (?,?,?)",
            (first_name, last_name, city),
        )
        conn.commit()
        return cur.lastrowid

def add_card(
    name: str,
    set_name: str,
    rarity: str,
    price_cents: int,
    stock: int = 0,
    db_path: Optional[str] = None,
) -> int:
    """Insert a new card and return the new row id."""

    with get_connection(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO cards(name, set_name, rarity, price_cents, stock) VALUES (?,?,?,?,?)",
            (name, set_name, rarity, price_cents, stock),
        )
        conn.commit()
        return cur.lastrowid


def list_cards(db_path: Optional[str] = None) -> Iterable[sqlite3.Row]:
    """Return all cards ordered by id."""

    with get_connection(db_path) as conn:
        cur = conn.execute(
            "SELECT id, name, set_name, rarity, price_cents, stock FROM cards ORDER BY id"
        )
        return cur.fetchall()


def list_emp(db_path: Optional[str] = None) -> Iterable[sqlite3.Row]:
    """Return all employees ordered by id."""

    with get_connection(db_path) as conn:
        cur = conn.execute(
            "SELECT id, first_name, last_name, city FROM employees ORDER BY id"
        )
        return cur.fetchall()

def get_card(identifier: str, db_path: Optional[str] = None) -> Optional[sqlite3.Row]:
    """Fetch a single card by numeric id or exact name."""
    
    with get_connection(db_path) as conn:
        if identifier.isdigit():
            cur = conn.execute(
                "SELECT id, name, set_name, rarity, price_cents, stock FROM cards WHERE id = ?",
                (int(identifier),),
            )
        else:
            cur = conn.execute(
                "SELECT id, name, set_name, rarity, price_cents, stock FROM cards WHERE name = ?",
                (identifier,),
            )
        return cur.fetchone()
    
def get_emp(identifier: int, db_path: Optional[str] = None) -> Optional[sqlite3.Row]:
    """Fetch a single employee by numeric id."""

    with get_connection(db_path) as conn:
        cur = conn.execute(
            "SELECT id, first_name, last_name, city FROM employees WHERE id = ?",
            (int(identifier),),
        )
        return cur.fetchone()

def update_card(
    identifier: str,
    *,
    name: Optional[str] = None,
    set_name: Optional[str] = None,
    rarity: Optional[str] = None,
    price_cents: Optional[int] = None,
    stock: Optional[int] = None,
    db_path: Optional[str] = None,
) -> int:
    """Update provided fields for a card located by id or name.

    Returns the number of affected rows.
    """

    fields = []
    values = []
    if name is not None:
        fields.append("name = ?")
        values.append(name)
    if set_name is not None:
        fields.append("set_name = ?")
        values.append(set_name)
    if rarity is not None:
        fields.append("rarity = ?")
        values.append(rarity)
    if price_cents is not None:
        fields.append("price_cents = ?")
        values.append(price_cents)
    if stock is not None:
        fields.append("stock = ?")
        values.append(stock)

    if not fields:
        # Nothing to update; signal no-op to caller.
        return 0

    with get_connection(db_path) as conn:
        if identifier.isdigit():
            values.append(int(identifier))
            cur = conn.execute(
                f"UPDATE cards SET {', '.join(fields)} WHERE id = ?",
                tuple(values),
            )
        else:
            values.append(identifier)
            cur = conn.execute(
                f"UPDATE cards SET {', '.join(fields)} WHERE name = ?",
                tuple(values),
            )
        conn.commit()
        return cur.rowcount

def update_emp(
    identifier: int,
    *,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    city: Optional[str] = None,
    db_path: Optional[str] = None,
) -> int:
    """
    Update provided fields for an employee located by id.

    Returns the number of affected rows.
    """
    fields = []
    values = []
    if first_name is not None:
        fields.append("first_name = ?")
        values.append(first_name)
    if last_name is not None:
        fields.append("last_name = ?")
        values.append(last_name)
    if city is not None:
        fields.append("city = ?")
        values.append(city)

    if not fields:
        # Nothing to update; signal no-op to caller.
        return 0

    with get_connection(db_path) as conn:
        values.append(int(identifier))
        cur = conn.execute(
            f"UPDATE employees SET {', '.join(fields)} WHERE id = ?",
            tuple(values),
        )
        conn.commit()
        return cur.rowcount

def delete_card(identifier: str, db_path: Optional[str] = None) -> int:
    """Delete a card by numeric id (string) or exact name. Returns rowcount."""

    with get_connection(db_path) as conn:
        if identifier.isdigit():
            cur = conn.execute("DELETE FROM cards WHERE id = ?", (int(identifier),))
        else:
            cur = conn.execute("DELETE FROM cards WHERE name = ?", (identifier,))
        conn.commit()
        return cur.rowcount

def delete_emp(identifier: int, db_path: Optional[str] = None) -> int:
    """Delete an employee by numeric id. Returns rowcount."""

    with get_connection(db_path) as conn:
        cur = conn.execute("DELETE FROM employees WHERE id = ?", (int(identifier),))
        conn.commit()
        return cur.rowcount

def test1(db_path: Optional[str] = None) -> Iterable[sqlite3.Row]:
    """Return all cards with price_cents >= 500."""
    
    with get_connection(db_path) as conn:
        cur = conn.execute(
            "SELECT id, name, set_name, rarity, price_cents, stock\
            FROM cards WHERE price_cents >= ?",
            (500,),
        )
        return cur.fetchall()
