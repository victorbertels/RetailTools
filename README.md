# Retail Tools Dashboard

A unified Streamlit dashboard for managing Deliverect retail tools.

## Features

1. **📦 Catalog Importer** - Import catalog structures from CSV files
2. **📊 Count Items in Menu** - Analyze menu items and their snooze status
3. **😴 Snooze History** - View snooze history for specific products (PLU)

## Setup

1. Make sure you have a virtual environment activated:
   ```bash
   source venv/bin/activate
   ```

2. Install dependencies (if not already installed):
   ```bash
   pip install -r catalogImporter/requirements.txt
   pip install pandas openpyxl  # For count items functionality
   ```

3. Make sure your `.env` file is set up with:
   ```
   CLIENT_ID=your_client_id
   CLIENT_SECRET=your_client_secret
   ```

## Running the App

From the project root directory:

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Usage

1. Select a tool from the sidebar
2. Enter the required parameters (Account ID, Location ID, etc.)
3. Click the action button to run the tool
4. View results and download data as needed

## Project Structure

```
RetailTools/
├── app.py                          # Main Streamlit dashboard
├── authentication/
│   └── tokening.py                 # Authentication functions
├── catalogImporter/
│   ├── app.py                      # Catalog importer Streamlit app
│   └── csvToCatalog.py             # CSV processing functions
├── countItemsInMenu/
│   └── countItems.py               # Menu analysis functions
└── snoozeHistory/
    └── snoozeHistoryPerPlu.py      # Snooze history functions
```

## Notes

- All tools require valid Deliverect API credentials
- Make sure your authentication is set up in `authentication/tokening.py`
- The dashboard uses Streamlit's session state to manage navigation

# RetailTools
