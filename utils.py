def cents_to_str(cents: int) -> str:
    """
    Converts cents to dollars.
    Example: 1099 -> "$ 10.99"
    """
    
    return f"$ {cents/100:.2f}"

def print_output(output) -> None:
    """Prints the output of a query."""

    for r in output:
        print(
            f"#{str(r['id']):>3} | {r['name']} | {r['set_name']} | {r['rarity']} | "
            f"{cents_to_str(r['price_cents'])} | stock = {r['stock']}"
        )