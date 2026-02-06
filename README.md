# Sales Data Printer

A simple and efficient Django application designed to track sales data, specifically "Money Received" and "Items Sold". It functionality to generate PDF reports and manage data via a user-friendly interface.

## Features

-   **Dashboard**: Easy navigation between different modules.
-   **Money Received**: Track incoming payments with date and amount.
-   **Items Sold**: Record sales with weight and price per unit details.
-   **Auto-Calculation**: Automatically calculates the total value (Weight * Price) for items sold.
-   **PDF Reports**: Generate comprehensive PDF reports including all data, using `xhtml2pdf`.
-   **Admin Panel**: Full administrative control to view, search, edit, and delete records.
-   **Auto-Settlement System**: Implements a First-In-First-Out (FIFO) logic where payments automatically close sales.
    -   **Closed Status**: Items are marked "Closed" when the running total of receipts covers them.
    -   **Settled Status**: Money entries are marked "Settled" when they have been fully utilized to close items.
    -   **Dynamic Totals**: Displays "Open/Unsettled" balances to clearly show outstanding amounts.
    -   **Detailed Reporting**: Toggle between viewing all records or only "open" sales.
20: -   **Database Management**:
21:     -   **Backup**: One-click "Quick Backup" creates a timestamped snapshot of your data.
22:     -   **Restore**: Manage and restore previous backups. Includes a **Safety First** mechanism that automatically backs up your *current* data before any restore operation, preventing accidental data loss.

## Tech Stack

-   **Backend**: Django 6.0+
-   **Database**: SQLite (Default)
-   **PDF Generation**: xhtml2pdf
-   **Frontend**: HTML5, Bootstrap 5

## Quick Start

1.  **Install Requirements**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Setup Environment**:
    Ensure `.env` file exists with `SECRET_KEY` and `DEBUG` settings (see `BUILD.md` for details).

3.  **Run Migrations**:
    ```bash
    python manage.py migrate
    ```

4.  **Start Server**:
    ```bash
    python manage.py runserver
    ```

Visit `http://127.0.0.1:8000/` to access the application.

## How to Test & Use Features

### 1. Advanced Verification: "Net Due" Calculation Logic
The Dashboard uses a smart calculation to show exactly what is owed for the currently viewed items, accounting for any "Unused" or "Advance" payments.

**The Formula:**
```
Net Due = (Sum of Filtered Open Items) - (Unused Money)
```
*Where:* `Unused Money = Total Money Received (Global) - Value of Closed Items`

**Scenario to Test:**
1.  **Setup**:
    *   You have sold 5 items worth **Rs. 5000** total.
    *   2 items (worth Rs. 2000) are "Closed" (fully paid).
    *   3 items (worth Rs. 3000) are "Open".
    *   You have received a total of **Rs. 2500**.
2.  **The Math**:
    *   Values of Closed Items = Rs. 2000.
    *   Unused Money (Advance) = Rs. 2500 (Total) - Rs. 2000 (Used) = **Rs. 500**.
    *   Filtered Total (Open Items) = **Rs. 3000**.
    *   **Net Due** = 3000 - 500 = **Rs. 2500**.
3.  **Verification**:
    *   Go to Dashboard.
    *   Filter for Open Items.
    *   Verify the **Net Due** matches this logic.

### 2. Comprehensive Test: Backup & Restore System
This system is designed to be fail-safe. Here is how to verify the safety mechanisms functionality:

**Phase A: Create a Checkpoint**
1.  Navigate to the Dashboard.
2.  Click the teal **Backup** button.
3.  **Verify**: Go to **Restore / Manage**. You should see a new backup file (e.g., `db_backup_2026-02-06_20-30...`) at the top of the list.

**Phase B: Simulate Data Loss/Change**
1.  Go to **Items Sold**.
2.  **Add** a new dummy record (e.g., Weight: 100, Price: 10, Total: 1000).
3.  **Verify**: The "Total Sales" on the dashboard should increase by 1000.

**Phase C: The Dangerous Restore (Simulated)**
1.  Go to **Restore / Manage**.
2.  Find the backup you created in **Phase A** (which *does not* have the dummy record).
3.  Click **Restore**.
4.  Accept the warning prompt.
5.  **Result**: You are redirected to the Dashboard.
6.  **Verify**: The dummy record is GONE. The "Total Sales" has reverted to the original amount.

**Phase D: The Safety Net (Recovery)**
1.  Go back to **Restore / Manage**.
2.  Look closely at the list. You will see a **new** file highlighted in yellow (or marked as "Safety Backup").
    *   Name format: `SAFETY_BACKUP_BEFORE_RESTORE_...`.
3.  This file captures the state *exactly before* you clicked Restore in Phase C (meaning it *contains* the dummy record).
4.  Click **Restore** on this `SAFETY_BACKUP` file.
5.  **Final Verification**: Go to Dashboard. The dummy record is **BACK**.

*This proves that even if you accidentally overwrite your database with an old backup, the system saved your work first.*

## Documentation

For detailed build, installation, and troubleshooting instructions, please refer to [BUILD.md](BUILD.md).
