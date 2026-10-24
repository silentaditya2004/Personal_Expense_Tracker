# Personal Expense Tracker

A beginner-friendly desktop expense tracker built with Python, Tkinter, SQLite, and Matplotlib.

## Features
- Add expenses with amount, category, date, and description
- Store records in a local SQLite database
- Search expenses by category, description, or date
- Filter the table by month (`YYYY-MM`)
- View all-time total, current-month total, and expense count
- View a pie chart of spending by category for a selected month
- Delete a selected record
- Export the currently filtered records to CSV for Excel

## Requirements
- Python 3.10 or newer recommended
- Tkinter (usually included with Python on Windows)
- Matplotlib

## Setup on Windows
1. Open this folder in VS Code.
2. Open **Terminal > New Terminal**.
3. Optional: create a virtual environment:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
4. Install dependencies:
   ```powershell
   py -m pip install -r requirements.txt
   ```
5. Run:
   ```powershell
   py main.py
   ```

If the `py` command does not work, try `python` instead.

## How to use
1. Enter an amount greater than zero.
2. Choose a category.
3. Enter the date in `YYYY-MM-DD` format.
4. Add a short description if you want.
5. Click **Add Expense**.
6. To filter by month, enter a value such as `2026-10` and click **Apply Month**.
7. Search text in the Search field. It matches category, description, and date.
8. Select a row and click **Delete Selected** to remove it.
9. Click **Export CSV** to save the currently filtered rows.

## Data and privacy
The application creates `expenses.db` in this folder on first launch. Expense data stays on your computer unless you choose to export or share it. Do not commit your personal `expenses.db` file to GitHub.

## Troubleshooting
- If charts do not show, run `py -m pip install matplotlib`.
- If Tkinter is missing, reinstall Python from python.org and ensure Tcl/Tk is included.
- If the app says a date is invalid, use `YYYY-MM-DD`, for example `2026-10-24`.
- If the month filter is invalid, use `YYYY-MM`, for example `2026-10`.
