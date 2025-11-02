def cents_to_str(cents: int) -> str:
    """
    Converts cents to dollars.
    Example: 1099 -> "$ 10.99"
    """

    return f"$ {cents/100:.2f}"


def _format_value(col: str, val) -> str:
    if val is None:
        return "NULL"
    # Apply friendly formatting for known columns
    if col == "price_cents":
        try:
            return cents_to_str(int(val))
        except Exception:
            return str(val)
    return str(val)


def print_table(rows) -> None:
    """
    Print sqlite3.Row results as a SQL-like table with headers.

    - Infers columns from the first row's keys()
    - Calculates widths from header and values
    - Prints header, separator, rows, and a row count
    """
    rows = list(rows)
    if not rows:
        print("(0 rows)")
        return

    # Determine columns from first row
    try:
        columns = list(rows[0].keys())
    except AttributeError:
        # Fallback if not sqlite3.Row: assume iterable of mappings
        columns = list(rows[0].keys())

    # Build string matrix and compute widths
    str_rows = []
    widths = [len(c) for c in columns]
    for r in rows:
        vals = [_format_value(col, r[col]) for col in columns]
        str_rows.append(vals)
        for i, v in enumerate(vals):
            if len(v) > widths[i]:
                widths[i] = len(v)

    # Helpers for rendering
    def fmt_row(vals):
        return " | ".join(val.ljust(widths[i]) for i, val in enumerate(vals))

    header = fmt_row(columns)
    separator = "-+-".join("-" * w for w in widths)

    print(header)
    print(separator)
    for vals in str_rows:
        print(fmt_row(vals))
    print(f"({len(rows)} rows)")