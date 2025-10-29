"""Command-line interface for the trading cards shop.

Provides CRUD operations backed by the SQLite helpers in ``db.py``.
Exposes a ``cards`` console script via ``pyproject.toml``.
"""

import argparse
from typing import Optional
from .utils import cents_to_str, print_output

from . import __all__  # noqa: F401  # ensures package import
from .db import (
    DEFAULT_DB_PATH,
    add_card,
    delete_card,
    get_card,
    init_db,
    list_cards,
    update_card,
    test1,
)

def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    """Build and parse CLI arguments.

    The optional ``argv`` is primarily for testing; when ``None`` defaults to
    ``sys.argv[1:]`` via ``ArgumentParser.parse_args``.
    """
    p = argparse.ArgumentParser(description="Trading card shop CLI (SQLite)")
    p.add_argument(
        "--db",
        default=DEFAULT_DB_PATH,
        help=f"Path to SQLite DB (default: {DEFAULT_DB_PATH})",
    )

    sub = p.add_subparsers(dest="cmd", required=True)

    s_init = sub.add_parser("init-db", help="Create tables and fills with sample cards")

    sub.add_parser("list", help="List all cards")

    s_get = sub.add_parser("get", help="Get a card by id or name")
    s_get.add_argument("identifier", help="Card id or exact name")

    s_add = sub.add_parser("add", help="Add a new card")
    s_add.add_argument("name")
    s_add.add_argument("set_name")
    s_add.add_argument("rarity")
    s_add.add_argument("price_cents", type=int)
    s_add.add_argument("--stock", type=int, default=0)

    s_upd = sub.add_parser("update", help="Update a card by id or name")
    s_upd.add_argument("identifier")
    s_upd.add_argument("--name")
    s_upd.add_argument("--set-name")
    s_upd.add_argument("--rarity")
    s_upd.add_argument("--price-cents", type=int)
    s_upd.add_argument("--stock", type=int)

    s_del = sub.add_parser("delete", help="Delete a card by id or name")
    s_del.add_argument("identifier")

    s_test1 = sub.add_parser("test1", help = "Run first test.")

    return p.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    """Entry point for the ``cards`` CLI.

    Returns a process exit code (0 for success, non-zero on not-found errors).
    """
    ns = parse_args(argv)
    db = ns.db

    if ns.cmd == "init-db":
        # Compute count before (if table doesn't exist yet, treat as 0)
        try:
            before = len(list_cards(db))
        except Exception:
            before = 0

        init_db(db)

        # Count after initialization and report delta
        after = len(list_cards(db))
        added = max(0, after - before)
        print(f"Initialized DB at {db}")
        print(f"Added {added} card(s)")
        return 0

    if ns.cmd == "list":
        rows = list_cards(db)
        if not rows:
            print("No cards found.")
            return 0
        print_output(rows)
        return 0

    if ns.cmd == "get":
        r = get_card(ns.identifier, db)
        if not r:
            print("Not found")
            return 1
        print_output([r])
        return 0

    if ns.cmd == "add":
        new_id = add_card(ns.name, ns.set_name, ns.rarity, ns.price_cents, ns.stock, db)
        print(f"Added card #{new_id}")
        return 0

    if ns.cmd == "update":
        # ``update_card`` accepts partial updates; only flags provided are changed.
        # ``identifier`` can be a numeric id or an exact name.
        updated = update_card(
            ns.identifier,
            name=ns.name,
            set_name=ns.set_name,
            rarity=ns.rarity,
            price_cents=ns.price_cents,
            stock=ns.stock,
            db_path=db,
        )
        print(f"Updated {updated} row(s)")
        return 0

    if ns.cmd == "delete":
        deleted = delete_card(ns.identifier, db)
        print(f"Deleted {deleted} row(s)")
        return 0
    
    if ns.cmd =="test1":
        out = test1(db)
        print_output(out)
        print("Ran test 1.")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
