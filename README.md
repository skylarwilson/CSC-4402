Trading Card Shop — SQLite + Python
===================================

Overview
--------
- Minimal SQLite schema with a few cards.
- Simple CLI for basic CRUD.
- Uses Python stdlib `sqlite3`.

Files
-----
- `cards/db.py`: DB schema, seed, and helpers.
- `cards/cli.py`: Argparse CLI to manage cards.
- `cards/__init__.py`: Package marker.
- `cards/__main__.py`: Enables `python -m cards`.
- `pyproject.toml`: Package metadata and `cards` console script.

Quick Start
-----------
Install from repo root. This installs a `cards` command on your PATH.

  `pip install -e .`

Initialize the database (with sample cards):

   `cards init-db`

List cards:

   `cards list`

Get a card by id or exact name:

   `cards get 1`
   
   `cards get "Flame Drake"`

Add a new card:

   `cards add "Sea Serpent" "Tidal Legends" Rare 499 --stock 3`

Update a card (by id or name):

   `cards update 1 --price-cents 1099 --stock 4`
   `cards update "Flame Drake" --price-cents 1099 --stock 4`

Delete a card:

   `cards delete 1`


Notes
-----
- Default DB path is `cards/shop.db` (created automatically).
