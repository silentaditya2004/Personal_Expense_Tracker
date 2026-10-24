import csv
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date, datetime
from pathlib import Path

try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
except ImportError:
    Figure = None
    FigureCanvasTkAgg = None


APP_TITLE = "Personal Expense Tracker"
DB_PATH = Path(__file__).resolve().parent / "expenses.db"
CATEGORIES = [
    "Food", "Transport", "Shopping", "Education", "Bills",
    "Health", "Entertainment", "Travel", "Other"
]


class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1180x760")
        self.root.minsize(950, 650)
        self.root.configure(bg="#f3f6fb")

        self.search_var = tk.StringVar()
        self.month_var = tk.StringVar(value=date.today().strftime("%Y-%m"))
        self.amount_var = tk.StringVar()
        self.category_var = tk.StringVar(value=CATEGORIES[0])
        self.date_var = tk.StringVar(value=date.today().isoformat())
        self.description_var = tk.StringVar()

        self._create_database()
        self._setup_style()
        self._build_ui()
        self.refresh_data()

    def _create_database(self):
        with sqlite3.connect(DB_PATH) as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    expense_date TEXT NOT NULL,
                    category TEXT NOT NULL,
                    amount REAL NOT NULL CHECK(amount > 0),
                    description TEXT NOT NULL DEFAULT ''
                )
            """)

    def _setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Treeview", rowheight=28, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("TButton", font=("Segoe UI", 10), padding=6)
        style.configure("TLabel", background="#f3f6fb", font=("Segoe UI", 10))
        style.configure("TLabelframe", background="#f3f6fb")
        style.configure("TLabelframe.Label", background="#f3f6fb",
                        font=("Segoe UI", 11, "bold"))

    def _build_ui(self):
        header = tk.Frame(self.root, bg="#172554", padx=22, pady=16)
        header.pack(fill="x")
        tk.Label(header, text="Personal Expense Tracker",
                 bg="#172554", fg="white",
                 font=("Segoe UI", 22, "bold")).pack(anchor="w")
        tk.Label(header, text="Record spending • Review monthly totals • Export reports",
                 bg="#172554", fg="#dbeafe",
                 font=("Segoe UI", 10)).pack(anchor="w", pady=(4, 0))

        main = tk.Frame(self.root, bg="#f3f6fb", padx=18, pady=14)
        main.pack(fill="both", expand=True)

        cards = tk.Frame(main, bg="#f3f6fb")
        cards.pack(fill="x", pady=(0, 12))
        self.total_card = self._summary_card(cards, "ALL-TIME SPENDING", "₹0.00", "#dbeafe")
        self.month_card = self._summary_card(cards, "THIS MONTH", "₹0.00", "#dcfce7")
        self.count_card = self._summary_card(cards, "NUMBER OF EXPENSES", "0", "#fef3c7")

        content = tk.Frame(main, bg="#f3f6fb")
        content.pack(fill="both", expand=True)

        left = ttk.LabelFrame(content, text="Add an expense", padding=12)
        left.pack(side="left", fill="y", padx=(0, 12))

        ttk.Label(left, text="Amount (₹)").grid(row=0, column=0, sticky="w", pady=(2, 4))
        self.amount_entry = ttk.Entry(left, textvariable=self.amount_var, width=25)
        self.amount_entry.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(left, text="Category").grid(row=2, column=0, sticky="w", pady=(2, 4))
        self.category_combo = ttk.Combobox(
            left, textvariable=self.category_var, values=CATEGORIES,
            state="readonly", width=22
        )
        self.category_combo.grid(row=3, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(left, text="Date (YYYY-MM-DD)").grid(row=4, column=0, sticky="w", pady=(2, 4))
        ttk.Entry(left, textvariable=self.date_var, width=25).grid(
            row=5, column=0, sticky="ew", pady=(0, 10)
        )

        ttk.Label(left, text="Description").grid(row=6, column=0, sticky="w", pady=(2, 4))
        ttk.Entry(left, textvariable=self.description_var, width=25).grid(
            row=7, column=0, sticky="ew", pady=(0, 12)
        )

        ttk.Button(left, text="Add Expense", command=self.add_expense).grid(
            row=8, column=0, sticky="ew", pady=3
        )
        ttk.Button(left, text="Clear Form", command=self.clear_form).grid(
            row=9, column=0, sticky="ew", pady=3
        )
        ttk.Button(left, text="Delete Selected", command=self.delete_selected).grid(
            row=10, column=0, sticky="ew", pady=3
        )
        ttk.Button(left, text="Export CSV", command=self.export_csv).grid(
            row=11, column=0, sticky="ew", pady=3
        )
        ttk.Label(left, text="Tip: select a row before deleting it.",
                  wraplength=190).grid(row=12, column=0, sticky="w", pady=(10, 0))

        right = tk.Frame(content, bg="#f3f6fb")
        right.pack(side="left", fill="both", expand=True)

        filters = ttk.LabelFrame(right, text="Search and monthly report", padding=10)
        filters.pack(fill="x", pady=(0, 10))
        ttk.Label(filters, text="Search").grid(row=0, column=0, sticky="w")
        search_entry = ttk.Entry(filters, textvariable=self.search_var, width=25)
        search_entry.grid(row=1, column=0, padx=(0, 10), sticky="ew")
        search_entry.bind("<KeyRelease>", lambda _event: self.refresh_data())

        ttk.Label(filters, text="Month (YYYY-MM)").grid(row=0, column=1, sticky="w")
        month_entry = ttk.Entry(filters, textvariable=self.month_var, width=15)
        month_entry.grid(row=1, column=1, padx=(0, 10), sticky="ew")
        month_entry.bind("<Return>", lambda _event: self.refresh_data())
        ttk.Button(filters, text="Apply Month", command=self.refresh_data).grid(
            row=1, column=2, padx=(0, 8)
        )
        ttk.Button(filters, text="Show All", command=self.show_all).grid(row=1, column=3)

        table_frame = ttk.LabelFrame(right, text="Expense history", padding=8)
        table_frame.pack(fill="both", expand=True)
        columns = ("id", "date", "category", "amount", "description")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        headings = {
            "id": "ID", "date": "Date", "category": "Category",
            "amount": "Amount (₹)", "description": "Description"
        }
        widths = {"id": 45, "date": 105, "category": 120, "amount": 110, "description": 220}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="w")
        self.tree.column("amount", anchor="e")
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        chart_frame = ttk.LabelFrame(right, text="Spending by category (selected month)", padding=8)
        chart_frame.pack(fill="x", pady=(10, 0))
        self.chart_holder = chart_frame
        self.chart_canvas = None
        self.chart_message = tk.Label(
            chart_frame, text="Add expenses to see your chart.",
            bg="#f3f6fb", fg="#475569", font=("Segoe UI", 10)
        )
        self.chart_message.pack(pady=8)

        footer = tk.Label(main, text=f"Data is saved locally in: {DB_PATH.name}",
                          bg="#f3f6fb", fg="#64748b", font=("Segoe UI", 9))
        footer.pack(anchor="w", pady=(8, 0))

    def _summary_card(self, parent, title, value, color):
        card = tk.Frame(parent, bg="white", highlightbackground="#dbe3ef", highlightthickness=1)
        card.pack(side="left", fill="x", expand=True, padx=(0, 10))
        tk.Label(card, text=title, bg="white", fg="#64748b",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=14, pady=(12, 4))
        value_label = tk.Label(card, text=value, bg="white", fg="#172554",
                               font=("Segoe UI", 19, "bold"))
        value_label.pack(anchor="w", padx=14, pady=(0, 12))
        return value_label

    def add_expense(self):
        raw_amount = self.amount_var.get().strip()
        raw_date = self.date_var.get().strip()
        category = self.category_var.get().strip()
        description = self.description_var.get().strip()

        try:
            amount = float(raw_amount)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid amount", "Enter an amount greater than 0, such as 125 or 49.50.")
            return

        try:
            parsed_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Invalid date", "Enter a valid date in YYYY-MM-DD format, for example 2026-10-24.")
            return

        if not category:
            messagebox.showerror("Missing category", "Please select an expense category.")
            return

        try:
            with sqlite3.connect(DB_PATH) as connection:
                connection.execute(
                    "INSERT INTO expenses (expense_date, category, amount, description) VALUES (?, ?, ?, ?)",
                    (parsed_date.isoformat(), category, amount, description)
                )
            self.clear_form()
            self.refresh_data()
            messagebox.showinfo("Saved", "Expense added successfully.")
        except sqlite3.Error as error:
            messagebox.showerror("Database error", f"Could not save the expense.\n{error}")

    def clear_form(self):
        self.amount_var.set("")
        self.category_var.set(CATEGORIES[0])
        self.date_var.set(date.today().isoformat())
        self.description_var.set("")
        self.amount_entry.focus_set()

    def show_all(self):
        self.search_var.set("")
        self.month_var.set("")
        self.refresh_data()

    def _get_filtered_rows(self):
        query = """
            SELECT id, expense_date, category, amount, description
            FROM expenses
            WHERE 1=1
        """
        params = []
        month = self.month_var.get().strip()
        search = self.search_var.get().strip()

        if month:
            if len(month) != 7 or month[4] != "-":
                raise ValueError("Month must use YYYY-MM format, such as 2026-10.")
            try:
                datetime.strptime(month, "%Y-%m")
            except ValueError:
                raise ValueError("Enter a valid month, such as 2026-10.")
            query += " AND substr(expense_date, 1, 7) = ?"
            params.append(month)

        if search:
            term = f"%{search}%"
            query += " AND (category LIKE ? OR description LIKE ? OR expense_date LIKE ?)"
            params.extend([term, term, term])

        query += " ORDER BY expense_date DESC, id DESC"
        with sqlite3.connect(DB_PATH) as connection:
            return connection.execute(query, params).fetchall()

    def refresh_data(self):
        try:
            rows = self._get_filtered_rows()
        except ValueError as error:
            messagebox.showwarning("Check month", str(error))
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in rows:
            self.tree.insert("", "end", values=(
                row[0], row[1], row[2], f"{row[3]:,.2f}", row[4]
            ))

        with sqlite3.connect(DB_PATH) as connection:
            all_total = connection.execute("SELECT COALESCE(SUM(amount), 0) FROM expenses").fetchone()[0]
            current_month = date.today().strftime("%Y-%m")
            month_total = connection.execute(
                "SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE substr(expense_date,1,7)=?",
                (current_month,)
            ).fetchone()[0]
            count = connection.execute("SELECT COUNT(*) FROM expenses").fetchone()[0]

        self.total_card.config(text=f"₹{all_total:,.2f}")
        self.month_card.config(text=f"₹{month_total:,.2f}")
        self.count_card.config(text=str(count))
        self._draw_chart()

    def _draw_chart(self):
        if self.chart_canvas is not None:
            self.chart_canvas.get_tk_widget().destroy()
            self.chart_canvas = None
        self.chart_message.pack_forget()

        month = self.month_var.get().strip()
        if not month:
            self.chart_message.config(text="Enter a month (YYYY-MM) to view its category chart.")
            self.chart_message.pack(pady=8)
            return

        try:
            datetime.strptime(month, "%Y-%m")
        except ValueError:
            self.chart_message.config(text="Use YYYY-MM format to display the chart.")
            self.chart_message.pack(pady=8)
            return

        with sqlite3.connect(DB_PATH) as connection:
            data = connection.execute("""
                SELECT category, SUM(amount)
                FROM expenses
                WHERE substr(expense_date,1,7)=?
                GROUP BY category
                ORDER BY SUM(amount) DESC
            """, (month,)).fetchall()

        if not data:
            self.chart_message.config(text=f"No expenses found for {month}.")
            self.chart_message.pack(pady=8)
            return

        if Figure is None or FigureCanvasTkAgg is None:
            self.chart_message.config(text="Charts need Matplotlib. Run: python -m pip install matplotlib")
            self.chart_message.pack(pady=8)
            return

        figure = Figure(figsize=(6.5, 2.3), dpi=90)
        axis = figure.add_subplot(111)
        labels = [item[0] for item in data]
        amounts = [item[1] for item in data]
        axis.pie(amounts, labels=labels, autopct="%1.1f%%", startangle=90, textprops={"fontsize": 8})
        axis.set_title(f"Category share — {month}", fontsize=10)
        figure.tight_layout()
        self.chart_canvas = FigureCanvasTkAgg(figure, master=self.chart_holder)
        self.chart_canvas.draw()
        self.chart_canvas.get_tk_widget().pack(fill="x", expand=False)

    def delete_selected(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Nothing selected", "Select an expense row in the table first.")
            return

        values = self.tree.item(selection[0], "values")
        expense_id = values[0]
        if not messagebox.askyesno("Confirm delete", f"Delete expense ID {expense_id}? This cannot be undone."):
            return

        try:
            with sqlite3.connect(DB_PATH) as connection:
                connection.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
            self.refresh_data()
            messagebox.showinfo("Deleted", "Expense deleted.")
        except sqlite3.Error as error:
            messagebox.showerror("Database error", f"Could not delete the expense.\n{error}")

    def export_csv(self):
        try:
            rows = self._get_filtered_rows()
        except ValueError as error:
            messagebox.showwarning("Check month", str(error))
            return

        if not rows:
            messagebox.showinfo("No data", "There are no expenses to export for the current filters.")
            return

        default_name = f"expenses_{date.today().isoformat()}.csv"
        path = filedialog.asksaveasfilename(
            title="Save expense report",
            defaultextension=".csv",
            initialfile=default_name,
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not path:
            return

        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Date", "Category", "Amount (INR)", "Description"])
                for row in rows:
                    writer.writerow(row)
            messagebox.showinfo("Export complete", f"Exported {len(rows)} expense(s) to:\n{path}")
        except OSError as error:
            messagebox.showerror("Export failed", f"Could not write the CSV file.\n{error}")


def main():
    root = tk.Tk()
    ExpenseTracker(root)
    root.mainloop()


if __name__ == "__main__":
    main()
