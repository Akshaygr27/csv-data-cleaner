from pathlib import Path
import re
import pandas as pd


EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def is_valid_email(value: str) -> bool:
    """Validate basic email format when a non-empty email is present."""
    if not value:
        return False
    return bool(EMAIL_PATTERN.match(value))


def parse_mandatory_columns(user_input: str, available_columns: list[str]) -> list[str]:
    """
    Parse comma-separated mandatory column names (case-insensitive match).
    Defaults to ['Name', 'Email'] if left blank.
    """
    if not user_input.strip():
        default_cols = [c for c in ["Name", "Email"] if c in available_columns]
        return default_cols

    col_lookup = {col.lower(): col for col in available_columns}
    requested = [part.strip() for part in user_input.split(",") if part.strip()]

    matched: list[str] = []
    unknown: list[str] = []
    for req in requested:
        actual = col_lookup.get(req.lower())
        if actual and actual not in matched:
            matched.append(actual)
        elif not actual:
            unknown.append(req)

    if unknown:
        print(f"Warning: Ignored unknown column(s): {', '.join(unknown)}")
    return matched


def clean_customer_csv(input_csv_path: str, mandatory_input: str = "") -> None:
    """Read a CSV, clean formatting, remove duplicates, validate rows, and export outputs."""
    cleaned_path_str = input_csv_path.strip().strip('"').strip("'")
    input_path = Path(cleaned_path_str).expanduser()

    if not input_path.exists() or not input_path.is_file():
        print(f"Error: File '{input_path}' was not found.")
        return

    try:
        # Read all fields as strings so IDs/phones don't lose leading zeros or become NaN
        df = pd.read_csv(input_path, dtype=str, keep_default_na=False)
    except (pd.errors.EmptyDataError, pd.errors.ParserError, OSError) as exc:
        print(f"Error reading CSV file: {exc}")
        return

    if df.empty:
        print("The CSV file contains headers or no data rows.")
        return

    # Clean column header whitespace
    df.columns = [col.strip() for col in df.columns]
    total_records = len(df)

    # Allow user to choose mandatory columns (default: Name, Email)
    mandatory_cols = parse_mandatory_columns(mandatory_input, list(df.columns))

    # 1. Trim whitespace and standardize text formatting
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()
        # Collapse multiple internal spaces
        df[col] = df[col].str.replace(r"\s+", " ", regex=True)

    # Standardize City capitalization (e.g., 'kochi' -> 'Kochi')
    city_col = next((c for c in df.columns if c.lower() == "city"), None)
    if city_col:
        df[city_col] = df[city_col].apply(lambda v: v.title() if v else v)

    # Normalize Email casing when present
    email_col = next((c for c in df.columns if c.lower() == "email"), None)
    if email_col:
        df[email_col] = df[email_col].str.lower()

    # 2. Identify and remove duplicate records (case-insensitive comparison across all columns)
    norm_key = df.apply(lambda row: tuple(val.lower() for val in row), axis=1)
    is_duplicate = norm_key.duplicated(keep="first")
    duplicates_removed = int(is_duplicate.sum())
    deduped_df = df[~is_duplicate].copy()

    # 3. Validate mandatory fields and email format
    valid_rows: list[dict[str, str]] = []
    invalid_rows: list[dict[str, str]] = []

    for _, row in deduped_df.iterrows():
        reasons: list[str] = []

        # Check mandatory columns
        missing_mandatory = [col for col in mandatory_cols if not row.get(col, "")]
        if missing_mandatory:
            reasons.append(f"Missing mandatory field(s): {', '.join(missing_mandatory)}")

        # Check email validity if Email column exists and has a value
        if email_col:
            email_val = row.get(email_col, "")
            if not email_val and email_col not in mandatory_cols:
                pass
            elif not is_valid_email(email_val):
                reasons.append(f"Invalid email format: '{email_val}'")

        if reasons:
            record = row.to_dict()
            record["Reason"] = "; ".join(reasons)
            invalid_rows.append(record)
        else:
            valid_rows.append(row.to_dict())

    output_dir = input_path.parent
    cleaned_file = output_dir / "cleaned_customers.csv"
    invalid_file = output_dir / "invalid_records.csv"

    cleaned_df = pd.DataFrame(valid_rows, columns=list(df.columns))
    invalid_df = pd.DataFrame(invalid_rows, columns=list(df.columns) + ["Reason"])

    try:
        cleaned_df.to_csv(cleaned_file, index=False)
        invalid_df.to_csv(invalid_file, index=False)
    except OSError as exc:
        print(f"Error writing output CSV files: {exc}")
        return

    # Display summary
    print("\n--- CSV Cleaning Summary ---")
    print(f"Total records processed : {total_records}")
    print(f"Duplicates removed      : {duplicates_removed}")
    print(f"Valid records           : {len(cleaned_df)}")
    print(f"Invalid records         : {len(invalid_df)}")
    print(f"\nSaved valid data to   : {cleaned_file}")
    print(f"Saved invalid data to : {invalid_file}")


if __name__ == "__main__":
    csv_path = input("Enter path to input CSV file: ")
    mandatory_cols_input = input(
        "Enter mandatory columns separated by commas (press Enter for default 'Name, Email'): "
    )
    clean_customer_csv(csv_path, mandatory_cols_input)