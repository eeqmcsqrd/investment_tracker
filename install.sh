#!/bin/bash

# Investment Tracker - Quick Installation Script
# This script will install all dependencies and verify the setup

echo "🚀 Investment Tracker - Installation Script"
echo "==========================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip."
    exit 1
fi

echo "✅ pip3 found: $(pip3 --version)"
echo ""

# Install requirements
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
else
    echo "❌ Failed to install dependencies. Please check the errors above."
    exit 1
fi

echo ""
echo "🔍 Verifying installation..."

# Verify key packages
python3 << END
import sys

packages = {
    'streamlit': 'Streamlit',
    'pandas': 'Pandas',
    'plotly': 'Plotly',
    'numpy': 'NumPy',
    'requests': 'Requests',
    'xlsxwriter': 'XlsxWriter',
    'openpyxl': 'OpenPyXL'
}

all_ok = True
for package, name in packages.items():
    try:
        __import__(package)
        print(f"✅ {name}")
    except ImportError:
        print(f"❌ {name}")
        all_ok = False

if all_ok:
    print("\n✅ All packages verified!")
    sys.exit(0)
else:
    print("\n❌ Some packages failed to install. Please check the errors.")
    sys.exit(1)
END

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Installation complete!"
    echo ""
    echo "To start the application, run:"
    echo "    streamlit run app_db.py"
    echo ""
    echo "📚 Documentation:"
    echo "  - READY_TO_RUN.md - Quick start guide"
    echo "  - OPTIMIZATION_SUMMARY.md - Technical details"
    echo "  - QUICK_IMPLEMENTATION_GUIDE.md - Implementation guide"
    echo ""
else
    echo ""
    echo "❌ Installation verification failed."
    echo "Please install missing packages manually:"
    echo "    pip3 install streamlit pandas plotly numpy requests xlsxwriter openpyxl"
fi
