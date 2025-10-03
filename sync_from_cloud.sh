#!/bin/bash
# sync_from_cloud.sh - Download database from Streamlit Cloud

echo "🔄 Investment Tracker - Cloud Sync"
echo "=================================="

# Backup local database
BACKUP_FILE="investment_data_backup_$(date +%Y%m%d_%H%M%S).db"
cp investment_data.db "$BACKUP_FILE"
echo "✅ Backup created: $BACKUP_FILE"

# Instructions
echo ""
echo "📥 Next steps:"
echo "1. Open your Streamlit Cloud app"
echo "2. Go to Settings tab"
echo "3. Click 'Download Database (.db)'"
echo "4. Save the file"
echo ""
echo "Then run: cp ~/Downloads/investment_data_*.db investment_data.db"
echo ""
echo "Or drag the downloaded file here and press Enter:"
read -r DOWNLOADED_FILE

if [ -f "$DOWNLOADED_FILE" ]; then
    cp "$DOWNLOADED_FILE" investment_data.db
    echo "✅ Database synced successfully!"
    echo ""
    echo "📊 Verifying..."
    python3 -c "import sqlite3; conn = sqlite3.connect('investment_data.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM investments'); print(f'Total records: {cursor.fetchone()[0]}'); conn.close()"
else
    echo "❌ File not found. Please try again."
fi
