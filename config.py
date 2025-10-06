# config.py
import os
try:
    # Optional dependency; avoid hard-failing if not installed
    from dotenv import load_dotenv  # type: ignore
except Exception:
    load_dotenv = None

# Load environment variables from .env file if python-dotenv is available
if load_dotenv:
    try:
        load_dotenv()
    except Exception:
        # Swallow any dotenv loading issues; environment vars may still be set by the OS
        pass

# API key for ExchangeRate API (v6)
API_KEY = os.getenv('API_KEY', '')  # Fallback to empty string if not found

# Cache duration for exchange rates (24 hours in seconds)
CACHE_DURATION = int(os.getenv('CACHE_DURATION', 86400))


# Ensure all keys are strings
INVESTMENT_ACCOUNTS = {str(k): v for k, v in {
    "Binance": "USD",
    "Trade Republic": "EUR",
    "Revolut - EUR": "EUR",
    "RBC": "CAD",
    "401k": "USD",
    "N26 - EUR": "EUR",
    "Revolut - USD": "USD",
    "Revolut - CLP": "CLP",
    "Revolut - CAD": "CAD",
    "WISE - EUR": "EUR",
    "WISE - USD": "USD",
    "WISE - CLP": "CLP",
    "WISE - CAD": "CAD",
    "RBC Bank Canada - CAD": "CAD",
    "RBC Bank Canada - USD": "USD",
    "RBC Bank Canada - EUR": "EUR",
    "RBC Bank US - USD": "USD",
    "HAPO Checking - USD": "USD",
    "HAPO Savings - USD": "USD",
    "Sui Wallet": "USD",
    "Phantom Wallet": "USD",
    "Ledger Wallet": "USD",
    "Talisman Wallet": "USD",
    # Add any additional accounts here
}.items()}

# Sustainability / Revolut constants
REVOLUT_EUR_ACCOUNT = "Revolut - EUR"
ENABLE_SUSTAINABILITY = True
SUSTAINABILITY_BASE_CURRENCY = "USD"

# Include Revolut *increases* as Income (decreases still counted as Expenses)
INCLUDE_REVOLUT_IN_INCOME = True

# Investment categories for grouping and visualization
INVESTMENT_CATEGORIES = {str(k): v for k, v in {
    "Binance": "Cryptocurrency",
    "Trade Republic": "Stocks",
    "Revolut - EUR": "Cash",
    "RBC": "Retirement",
    "401k": "Retirement",
    "N26 - EUR": "Cash",
    "Revolut - USD": "Cash",
    "Revolut - CLP": "Cash",
    "Revolut - CAD": "Cash",
    "WISE - EUR": "Cash",
    "WISE - USD": "Cash",
    "WISE - CLP": "Cash",
    "WISE - CAD": "Cash",
    "RBC Bank Canada - CAD": "Banking",
    "RBC Bank Canada - USD": "Banking",
    "RBC Bank Canada - EUR": "Banking",
    "RBC Bank US - USD": "Banking",
    "HAPO Checking - USD": "Banking",
    "HAPO Savings - USD": "Savings",
    "Sui Wallet": "Cryptocurrency",
    "Phantom Wallet": "Cryptocurrency",
    "Ledger Wallet": "Cryptocurrency",
    "Talisman Wallet": "Cryptocurrency",
    # Add any additional categories here
}.items()}

# Tracked investments for performance comparison
# These are TRUE INVESTMENTS (exclude bank balances/cash accounts)
TRACKED_INVESTMENTS = [
    'RBC',           # Retirement account
    'Binance',       # Crypto exchange
    '401k',          # Retirement account
    'Ledger Wallet'  # Crypto wallet
]

# Ensure tracked investments are strings
TRACKED_INVESTMENTS = [str(inv) for inv in TRACKED_INVESTMENTS]

# Investment accounts only (for pure performance tracking)
# Excludes: Bank balances, cash accounts, spending money
INVESTMENT_ACCOUNTS_ONLY = TRACKED_INVESTMENTS  # Same list for now

# Data file settings
DATA_FILE = 'investment_data.csv'
BACKUP_FOLDER = 'backups'