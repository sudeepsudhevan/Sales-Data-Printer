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
    -   **Dashboard Toggle**: Filter to show or hide closed/settled historical records.

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

## Documentation

For detailed build, installation, and troubleshooting instructions, please refer to [BUILD.md](BUILD.md).
