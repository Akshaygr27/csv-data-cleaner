# CSV Data Cleaner

A Python tool powered by Pandas that cleans messy customer CSV files by removing duplicates, standardizing text formatting, validating mandatory fields and email addresses, and exporting separate valid and invalid record reports.

## Features

- **Text & Formatting Standardization:** Trims leading/trailing whitespace, collapses extra internal spaces, title-cases `City` values, and normalizes `Email` casing.
- **Duplicate Detection & Removal:** Identifies and removes duplicate rows (including case-insensitive matches after formatting) while tracking how many duplicates were dropped.
- **Configurable Mandatory Columns & Validation:** Lets users specify mandatory columns at runtime (defaulting to `Name, Email`) and validates email format with regular expressions.
- **Cleaned Output & Rejection Report:** Exports valid rows to `cleaned_customers.csv` and rejected rows with failure reasons to `invalid_records.csv`, alongside a console summary.

## Tech Stack

- **Python 3** (`pathlib`, `re`)
- **pandas**

## Getting Started

### Prerequisites

- Python 3.9 or higher and `pandas` installed.

### Installation & Usage

1. Clone or download the repository and open a terminal in the project folder:

   ```bash
   git clone <your-repo-url>
   cd <your-repo-folder>
   pip install pandas

2. Run

    python csv_data_cleaner.py