# Manual test cases

Use sample data only while testing.

| No. | Test | Expected result |
|---|---|---|
| 1 | Add amount 120, Food, today's date, "Lunch" | Expense is saved and appears in the table |
| 2 | Add amount 0 | Validation message appears; record is not saved |
| 3 | Add amount "abc" | Validation message appears; record is not saved |
| 4 | Enter date `24-10-2026` | Date validation message appears |
| 5 | Search `Lunch` | Matching expense appears |
| 6 | Apply month `2026-10` | Only October 2026 records appear |
| 7 | Select a row and delete it | Confirmation appears; record is removed if confirmed |
| 8 | Export CSV | A CSV file is saved with headers and visible filtered records |
| 9 | Close and reopen app | Previously saved expenses remain |
| 10 | Choose a month with no expenses | Chart area says no expenses found |
