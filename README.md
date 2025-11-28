Trading Card Shop — SQLite + Python
===================================

Overview
--------
- Minimal SQLite schema with cards and employees.
- Simple CLI.
- Uses Python stdlib `sqlite3`.
- Requires Python >= 3.8.

Quick Start
-----------
Clone the repo.

  `git clone https://github.com/skylarwilson/CSC-4402`

Install from repo root. This enables the `cards` command.

  `pip install -e .`

Initialize the database and seed sample data:

   `cards init-db`

List cards:

   `cards list_c`

Get a card by id or exact name:

   `cards get 1`
   
   `cards get "Flame Drake"`

Add a new card:

   `cards add "Sea Serpent" "Tidal Legends" Rare 499 --stock 3`

Update a card (by id or name):

   `cards update 1 --price-cents 1099 --stock 4`
   
   `cards update "Sea Serpent" --price-cents 1099 --stock 4`

Delete a card:

   `cards delete 1`
