
# Modern Investment and Expense Tracker

This is a Streamlit web application that serves as a personal investment and expense tracker. The app enables users to:

* Input and manage investment and expense data
* Track performance over time
* Compare investments and expenses against each other and external benchmarks
* Visualize insights via interactive graphs, charts, and dashboards

This application is a complete rewrite of the original, focusing on performance, modularity, and new features.

## Setup and Usage

1. **Install dependencies:**
   ```
   pip install -r requirements_new.txt
   ```

2. **Run the application:**
   ```
   streamlit run app_new.py
   ```

## New Features

* **SQLite Backend:** The application now uses a robust SQLite backend instead of CSV files for better performance and scalability.
* **Dark/Light Mode:** You can now switch between dark and light themes using the toggle in the sidebar.
* **Exportable Reports:** The dashboard can be exported as an HTML file.
* **Benchmark Comparison:** A new "Benchmark" tab allows you to compare your portfolio performance against major stock indices like the S&P 500, NASDAQ, and Dow Jones.
