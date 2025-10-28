"""Helper for generating pseudo-random trading card rows.

Used by ``init_db`` to seed sample data and optionally runnable as a module
to insert additional cards into an existing database.
"""

import random
from typing import Iterable, Iterator, List, Sequence, Tuple, Optional


# A card tuple matches the `cards` table insert order in db.py
# (name, set_name, rarity, price_cents, stock)
CardRow = Tuple[str, str, str, int, int]


ADJECTIVES: Sequence[str] = (
    "Flame", "Shadow", "Crystal", "Thunder", "Silver", "Vorpal", "Elder",
    "Ancient", "Mystic", "Phantom", "Gilded", "Searing", "Frost", "Arcane",
)

NOUNS: Sequence[str] = (
    "Drake", "Golem", "Sage", "Warden", "Ranger", "Phoenix", "Titan",
    "Sprite", "Hydra", "Knight", "Serpent", "Djinn", "Colossus", "Revenant",
)

SUFFIXES: Sequence[str] = (
    " of Dawn", " of the Vale", " of Embers", " of Echoes", ", the Unbound",
    " of Shards", " of Storms", " of Twilight", ", Worldshaper", " of Cinders",
    " of Frost", ", Soulbinder", " of Horizons",
)

SET_NAMES: Sequence[str] = (
    "Embers Rising", "Verdant Vale", "Shattered Realms", "Twilight Citadel",
    "Stormcall Saga", "Gilded Empires", "Frozen Expanse",
)

RARITIES: Sequence[str] = ("Common", "Uncommon", "Rare", "Mythic")


def _price_for_rarity(rarity: str, rng: random.Random) -> int:
    if rarity == "Common":
        return rng.randint(50, 199)
    if rarity == "Uncommon":
        return rng.randint(200, 499)
    if rarity == "Rare":
        return rng.randint(500, 1499)
    # Mythic
    return rng.randint(1500, 3999)


def _weighted_rarity(rng: random.Random) -> str:
    # Approximate distribution: Common 55%, Uncommon 30%, Rare 12%, Mythic 3%
    roll = rng.random()
    if roll < 0.55:
        return "Common"
    if roll < 0.85:
        return "Uncommon"
    if roll < 0.97:
        return "Rare"
    return "Mythic"


def generate_cards(count: int = 25, seed: Optional[int] = None) -> List[CardRow]:
    """Generate a list of pseudo-random card rows.

    - Ensures unique names within this generated batch.
    - Uses weighted rarities and rarity-based price ranges.
    """
    rng = random.Random(seed)
    names_seen = set()
    out: List[CardRow] = []

    # Cap attempts to avoid infinite loops if count is huge vs. name space
    attempts = 0
    while len(out) < count and attempts < count * 20:
        attempts += 1
        name = f"{rng.choice(ADJECTIVES)} {rng.choice(NOUNS)}{rng.choice(SUFFIXES)}"
        if name in names_seen:
            continue
        names_seen.add(name)

        set_name = rng.choice(SET_NAMES)
        rarity = _weighted_rarity(rng)
        price_cents = _price_for_rarity(rarity, rng)
        stock = rng.randint(0, 20 if rarity in ("Rare", "Mythic") else 50)

        out.append((name, set_name, rarity, price_cents, stock))

    return out


if __name__ == "__main__":
    # Optional CLI helper to populate an existing DB with more cards.
    # Usage: python -m cards.gen_data --db path --count 50 --seed 42
    import argparse
    from . import db as dbmod  # Imported only for CLI mode to avoid cycles.

    ap = argparse.ArgumentParser(description="Generate and insert fake cards")
    ap.add_argument("--db", default=None, help="Path to DB file (defaults to package default)")
    ap.add_argument("--count", type=int, default=25, help="How many cards to generate")
    ap.add_argument("--seed", type=int, default=None, help="Optional RNG seed for reproducibility")
    args = ap.parse_args()

    rows = generate_cards(count=args.count, seed=args.seed)
    inserted = 0
    for name, set_name, rarity, price_cents, stock in rows:
        try:
            dbmod.add_card(name, set_name, rarity, price_cents, stock, db_path=args.db)
            inserted += 1
        except Exception:
            # Ignore duplicates or constraint failures when running repeatedly
            pass

    print(f"Inserted {inserted} generated cards into {args.db or dbmod.DEFAULT_DB_PATH}")
