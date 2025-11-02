"""Command-line interface for the trading cards shop.

Provides CRUD operations backed by the SQLite helpers in ``db.py``.
Exposes a ``cards`` console script via ``pyproject.toml``.
"""

import argparse
from typing import Optional
from .utils import print_table
from test_scripts.test_cli import test_cli

from . import __all__  # noqa: F401  # ensures package import
from . import db

def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    """Build and parse CLI arguments.

    The optional ``argv`` is primarily for testing; when ``None`` defaults to
    ``sys.argv[1:]`` via ``ArgumentParser.parse_args``.
    """
    p = argparse.ArgumentParser(description="Trading card shop CLI (SQLite)")
    # Global options
    p.add_argument(
        "--db",
        default=db.DEFAULT_DB_PATH,
        help=f"Path to SQLite DB (default: {db.DEFAULT_DB_PATH})",
    )

    sub = p.add_subparsers(dest="cmd", required=True)

    # INIT-DB
    # initialize the database with tables and data
    s_init = sub.add_parser("init-db", help="Create tables and fills with sample cards")



    # RUN TEST SCRIPT
    test_script = sub.add_parser("test_cli", help="Run test script for correctness")



    # LIST
    list_c = sub.add_parser("list_c", help="List all cards")
    list_e = sub.add_parser("list_e", help="List all employees")
    # list_order = sub.add_parser("list_o", help="List all orders")
    # list_pr = sub.add_parser("list_pr", help="List all products")
    # list_pay = sub.add_parser("list_pr", help="List all products")
    # list_inv = sub.add_parser("list_pr", help="List all products")



    # GET
    c_get = sub.add_parser("get", help="Get a card by id or name")
    c_get.add_argument("identifier", help="Card id or exact name")
    get_emp = sub.add_parser("get_emp", help="Get an employee by id")
    get_emp.add_argument("identifier", help="Employee id")



    # ADD
    c_add = sub.add_parser("add", help="Add a new card")
    c_add.add_argument("name")
    c_add.add_argument("set_name")
    c_add.add_argument("rarity")
    c_add.add_argument("price_cents", type=int)
    c_add.add_argument("--stock", type=int, default=0)


    s_add_emp = sub.add_parser("add_emp", help="Add a new employee")
    s_add_emp.add_argument("id")
    s_add_emp.add_argument("first_name")
    s_add_emp.add_argument("last_name")
    s_add_emp.add_argument("city")



    # UPDATE
    s_upd = sub.add_parser("update", help="Update a card by id or name")
    s_upd.add_argument("identifier")
    s_upd.add_argument("--name")
    s_upd.add_argument("--set-name")
    s_upd.add_argument("--rarity")
    s_upd.add_argument("--price-cents", type=int)
    s_upd.add_argument("--stock", type=int)

    e_upd = sub.add_parser("update_e", help="Update an employee by id")
    e_upd.add_argument("identifier")
    e_upd.add_argument("--first_name")
    e_upd.add_argument("--last_name")
    e_upd.add_argument("--city")

    # DELETE
    s_del = sub.add_parser("delete", help="Delete a card by id or name")
    s_del.add_argument("identifier")

    emp_del = sub.add_parser("delete_e", help="Delete an employee by id")
    emp_del.add_argument("identifier")


    # TEST QUERIES
    s_test1 = sub.add_parser("test1", help = "Run first test.")
    s_test2 = sub.add_parser("test2", help = "Run second test.")

    return p.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    """Entry point for the ``cards`` CLI.

    Returns a process exit code (0 for success, non-zero on not-found errors).
    """
    ns = parse_args(argv)
    db_path = ns.db

    if ns.cmd == "init-db":
        # Compute count before (if table doesn't exist yet, treat as 0)
        try:
            before = len(db.list_cards(db_path))
        except Exception:
            before = 0

        db.init_db(db_path)

        print(f"Initialized DB at {db}")
        return 0

    if ns.cmd == "list_c":
        rows = db.list_cards(db_path)
        if not rows:
            print("No cards found.")
            return 0
        print_table(rows)
        return 0
    
    if ns.cmd == "list_e":
        rows = db.list_emp(db_path)
        if not rows:
            print("No employees found.")
            return 0
        print_table(rows)
        return 0

    if ns.cmd == "get":
        r = db.get_card(ns.identifier, db_path)
        if not r:
            print("Not found")
            return 1
        print_table([r])
        return 0
    
    if ns.cmd == "get_emp":
        r = db.get_emp(ns.identifier, db_path)
        if not r:
            print("Not found")
            return 1
        print_table([r])
        return 0

    if ns.cmd == "add":
        new_id = db.add_card(ns.name, ns.set_name, ns.rarity, ns.price_cents, ns.stock, db_path)
        print(f"Added card #{new_id}")
        return 0
    
    if ns.cmd == "add_emp":
        new_id = db.add_emp(ns.first_name, ns.last_name, ns.city, db_path)
        print(f"Added employee #{new_id}")
        return 0



    # UPDATE
    if ns.cmd == "update":
        # ``update_card`` accepts partial updates; only flags provided are changed.
        # ``identifier`` can be a numeric id or an exact name.
        updated = db.update_card(
            ns.identifier,
            name=ns.name,
            set_name=ns.set_name,
            rarity=ns.rarity,
            price_cents=ns.price_cents,
            stock=ns.stock,
            db_path=db_path,
        )
        print(f"Updated {updated} row(s)")
        return 0
    
    if ns.cmd == "update_e":
        updated = db.update_emp(
            ns.identifier,
            first_name=ns.first_name,
            last_name=ns.last_name,
            city=ns.city,
            db_path=db_path,
        )
        print(f"Updated {updated} row(s)")
        return 0

    if ns.cmd == "delete":
        deleted = db.delete_card(ns.identifier, db_path)
        print(f"Deleted {deleted} row(s)")
        return 0
    
    if ns.cmd == "delete_e":
        deleted = db.delete_emp(ns.identifier, db_path)
        print(f"Deleted {deleted} row(s)")
        return 0
    
    if ns.cmd =="test1":
        out = db.test1(db_path)
        print_table(out)
        print("Ran test 1.")
        return 0
    
    if ns.cmd =="test2":
        out = db.test2(db_path)
        print_table(out)
        print("Ran test 2.")
        return 0
    



    if ns.cmd =="test_cli":
        test_cli()
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
