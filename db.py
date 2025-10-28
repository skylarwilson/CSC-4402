"""SQLite helpers for the trading cards shop.

This module encapsulates DB access: connection management, schema creation,
and CRUD helpers for the ``cards`` table. It intentionally uses only the
stdlib ``sqlite3`` module and returns ``sqlite3.Row`` objects for convenient
dict-like access in the CLI.
"""

import os
import sqlite3
from typing import Iterable, Optional


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
"""


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Open a connection with row_factory set to ``sqlite3.Row``.

    Ensures the parent directory for the DB file exists so first-time usage
    works without needing to create folders manually.
    """
    path = db_path or DEFAULT_DB_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Optional[str] = None, with_sample: bool = True) -> None:
    """Create tables if missing and optionally seed sample data.

    Sample data is only inserted when the ``cards`` table is empty, and is
    generated via ``gen_data.generate_cards`` when available.
    """
    with get_connection(db_path) as conn:
        conn.executescript(SCHEMA_SQL)
        if with_sample:
            # Seed only via generator when table is empty
            cur = conn.execute("SELECT COUNT(1) AS c FROM cards")
            if cur.fetchone()[0] == 0:
                try:
                    from .gen_data import generate_cards  # type: ignore
                except Exception:
                    generate_cards = None
                if generate_cards is not None:
                    rows = generate_cards(count=25)
                    if rows:
                        conn.executemany(
                            "INSERT OR IGNORE INTO cards(name, set_name, rarity, price_cents, stock) VALUES (?,?,?,?,?)",
                            rows,
                        )
        conn.commit()


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


def get_card(identifier: str, db_path: Optional[str] = None) -> Optional[sqlite3.Row]:
    """Fetch a single card by numeric id (string) or exact name."""
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

    Only non-None keyword arguments are included in the UPDATE statement. The
    SQL uses parameter binding for values; the dynamic portion is limited to
    the column list built from a fixed, vetted set which avoids injection.
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


def delete_card(identifier: str, db_path: Optional[str] = None) -> int:
    """Delete a card by numeric id (string) or exact name. Returns rowcount."""
    with get_connection(db_path) as conn:
        if identifier.isdigit():
            cur = conn.execute("DELETE FROM cards WHERE id = ?", (int(identifier),))
        else:
            cur = conn.execute("DELETE FROM cards WHERE name = ?", (identifier,))
        conn.commit()
        return cur.rowcount
