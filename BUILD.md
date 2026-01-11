# How to Build and Run Sales Data Printer

This guide will help you set up and run the Sales Data Printer application on your local machine.

## Prerequisites

- **Python 3.8+**: Ensure Python is installed and added to your PATH.

## Installation

1.  **Clone/Navigate** to the project directory:
    ```bash
    cd "e:\New Projects\Sale-Data-Printer"
    ```

2.  **Install Dependencies**:
    ```bash
    pip install django xhtml2pdf
    ```

3.  **Apply Database Migrations**:
    ```bash
    python manage.py migrate
    ```

## Running the Application

1.  **Start the Server**:
    ```bash
    python manage.py runserver
    ```

2.  **Access the App**:
    Open your browser and go to `http://127.0.0.1:8000/`.

## Usage

- **Money Received**: Go to the "Money Received" tab to add records of payments.
- **Item Sold**: Go to the "Item Sold" tab to add sold items. The total (Weight * Price) is calculated automatically.
- **Print PDF**: Click "Print Full PDF" in the navigation bar to generate a PDF report of all data.

## Admin Interface

To manage data directly:

1.  **Create a Superuser** (if you haven't already):
    ```bash
    python manage.py createsuperuser
    ```
    Follow the prompts to set a username and password.

2.  **Access Admin**:
    Go to `http://127.0.0.1:8000/admin/` and log in.
