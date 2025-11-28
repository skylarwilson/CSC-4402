"""Command-line interface for our Trading Cards shop."""


import argparse
from typing import List, Optional
from .utils import print_table
from . import __all__
from . import db


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """Build and parse CLI arguments."""

    p = argparse.ArgumentParser(description="Trading Card shop CLI tool")
    p.add_argument(
        "--db",
        default=db.DEFAULT_DB_PATH,
        help=f"Path to SQLite DB (default: {db.DEFAULT_DB_PATH})",
    )
    sub = p.add_subparsers(dest="cmd", required=True)


    # INIT-DB
    # Initialize the database with tables and data
    init = sub.add_parser("init-db", help="Create tables and fills with sample data")


    # LIST
    list_c = sub.add_parser("list_c", help="List all cards")
    list_e = sub.add_parser("list_e", help="List all employees")


    # GET
    get_c = sub.add_parser("get", help="Get a card by id or name")
    get_c.add_argument("identifier", help="Card id or exact name")
    get_emp = sub.add_parser("get_emp", help="Get an employee by id")
    get_emp.add_argument("identifier", type=int, help="Employee id")


    # ADD
    add_c = sub.add_parser("add", help="Add a new card")
    add_c.add_argument("name")
    add_c.add_argument("set_name")
    add_c.add_argument("rarity")
    add_c.add_argument("price_cents", type=int)
    add_c.add_argument("--stock", type=int, default=0)

    add_emp = sub.add_parser("add_emp", help="Add a new employee")
    add_emp.add_argument("first_name")
    add_emp.add_argument("last_name")
    add_emp.add_argument("city")


    # UPDATE
    upd_c = sub.add_parser("update", help="Update a card by id or name")
    upd_c.add_argument("identifier")
    upd_c.add_argument("--name")
    upd_c.add_argument("--set-name")
    upd_c.add_argument("--rarity")
    upd_c.add_argument("--price-cents", type=int)
    upd_c.add_argument("--stock", type=int)

    upd_emp = sub.add_parser("update_e", help="Update an employee by id")
    upd_emp.add_argument("identifier", type=int)
    upd_emp.add_argument("--first_name")
    upd_emp.add_argument("--last_name")
    upd_emp.add_argument("--city")


    # DELETE
    del_c = sub.add_parser("delete", help="Delete a card by id or name")
    del_c.add_argument("identifier")

    del_emp = sub.add_parser("delete_e", help="Delete an employee by id")
    del_emp.add_argument("identifier", type=int)


    # TEST QUERIES
    test1 = sub.add_parser("test1", help = "Run first test.")

    return p.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    """Entry point for the `cards` CLI.

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

        print(f"Initialized DB at {db_path}")
        return 0


    # LIST
    # List cards
    if ns.cmd == "list_c":
        rows = db.list_cards(db_path)
        if not rows:
            print("No cards found.")
            return 0
        print_table(rows)
        return 0
    
    # List employees
    if ns.cmd == "list_e":
        rows = db.list_emp(db_path)
        if not rows:
            print("No employees found.")
            return 0
        print_table(rows)
        return 0


    # GET
    # Get card by id or name
    if ns.cmd == "get":
        r = db.get_card(ns.identifier, db_path)
        if not r:
            print("Not found")
            return 1
        print_table([r])
        return 0
    
    # Get employee by id
    if ns.cmd == "get_emp":
        r = db.get_emp(ns.identifier, db_path)
        if not r:
            print("Not found")
            return 1
        print_table([r])
        return 0


    # ADD
    # Add a new card
    if ns.cmd == "add":
        new_id = db.add_card(ns.name, ns.set_name, ns.rarity, ns.price_cents, ns.stock, db_path)
        print(f"Added card #{new_id}")
        return 0
    
    # Add a new employee
    if ns.cmd == "add_emp":
        new_id = db.add_emp(ns.first_name, ns.last_name, ns.city, db_path)
        print(f"Added employee #{new_id}")
        return 0


    # UPDATE
    # Update a card by id or name
    if ns.cmd == "update":
        # `identifier` can be a numeric id or an exact name.
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
    
    # Update an employee by id
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


    # DELETE
    # Delete a card by id or name
    if ns.cmd == "delete":
        deleted = db.delete_card(ns.identifier, db_path)
        print(f"Deleted {deleted} row(s)")
        return 0
    
    # Delete an employee by id
    if ns.cmd == "delete_e":
        deleted = db.delete_emp(ns.identifier, db_path)
        print(f"Deleted {deleted} row(s)")
        return 0


    # TEST QUERIES
    # Initialize test1
    if ns.cmd == "test1":
        out = db.test1(db_path)
        print_table(out)
        print("Ran test 1.")
        return 0


    return 1


if __name__ == "__main__":
    raise SystemExit(main())
