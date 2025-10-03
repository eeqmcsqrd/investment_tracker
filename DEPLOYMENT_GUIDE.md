# Investment Tracker - Mobile Deployment Guide

This guide will help you deploy your investment tracker to Streamlit Cloud for free mobile access.

## Prerequisites
- GitHub account (free)
- Streamlit Cloud account (free - sign up at share.streamlit.io)
- Your investment tracker files

## Step 1: Prepare Your Repository

### 1.1 Create a GitHub Repository
1. Go to github.com and create a new repository (e.g., "investment-tracker")
2. Make it **PRIVATE** to keep your financial data secure
3. Don't initialize with README (we'll push existing code)

### 1.2 Initialize Git and Push Your Code
```bash
cd /Users/io/Downloads/investment_tracker

# Initialize git repository
git init

# Create .gitignore to exclude sensitive files
cat > .gitignore << 'GITIGNORE'
# Environment and secrets
.env
*.env

# Data files (we'll sync these separately)
investment_data.db
investment_data.csv
backups/
benchmarks_cache.json

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
GITIGNORE

# Add all files
git add .

# Commit
git commit -m "Initial commit - Investment Tracker"

# Add remote (replace YOUR_USERNAME and YOUR_REPO)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Push to GitHub
git push -u origin main
```

## Step 2: Deploy to Streamlit Cloud

### 2.1 Sign Up for Streamlit Cloud
1. Go to https://share.streamlit.io
2. Sign in with your GitHub account
3. Authorize Streamlit to access your repositories

### 2.2 Create New App
1. Click "New app" button
2. Select your repository: `YOUR_USERNAME/YOUR_REPO`
3. Select branch: `main`
4. Select main file: `app_db.py`
5. Click "Deploy"

### 2.3 Configure Secrets (API Keys)
1. In Streamlit Cloud dashboard, click on your app
2. Go to Settings → Secrets
3. Add your secrets in TOML format:

```toml
# Your ExchangeRate API key
API_KEY = "your_api_key_here"

# Optional: Authentication password
AUTH_PASSWORD = "your_secure_password_here"
```

4. Save secrets

## Step 3: Upload Your Data

Since we excluded `investment_data.db` from git (for security), you need to upload it:

### Option A: Use Streamlit Cloud File Upload (Recommended)
1. Your app will detect missing database
2. Use the built-in file uploader in the app to upload your `.db` file
3. Data will persist in Streamlit Cloud storage

### Option B: Manual Upload via GitHub
1. Create a new branch: `git checkout -b data-upload`
2. Temporarily add data: `git add -f investment_data.db`
3. Commit: `git commit -m "Add initial data"`
4. Push: `git push origin data-upload`
5. In Streamlit Cloud, redeploy from `data-upload` branch
6. After deployment, switch back to `main` branch

### Option C: Use Google Drive Sync (see below)

## Step 4: Access Your App

Your app will be available at:
```
https://YOUR_USERNAME-YOUR_REPO-app-db-HASH.streamlit.app
```

Save this URL to your mobile device home screen for quick access.

## Step 5: Enable Authentication (Optional but Recommended)

To add password protection, see `auth_wrapper.py` and follow instructions in AUTHENTICATION_GUIDE.md.

## Updating Your Data Remotely

### Method 1: Direct Entry in App
- Use the "Data" tab to manually add new entries
- Data is saved automatically to the cloud database

### Method 2: Upload Updated Database
- Export your local database
- Use app's file upload feature to replace cloud database

### Method 3: Google Drive Sync (Advanced)
See GOOGLE_DRIVE_SYNC.md for automated synchronization setup.

## Troubleshooting

### App Won't Start
- Check "Manage app" → "Logs" for errors
- Verify all dependencies in requirements.txt
- Ensure secrets are properly configured

### Missing Data
- Verify database file was uploaded
- Check app logs for database connection errors

### Slow Performance
- First load may be slow (cold start)
- Subsequent loads are faster
- Consider reducing date range for better performance

### Authentication Not Working
- Verify AUTH_PASSWORD is set in Secrets
- Clear browser cache and retry

## Security Best Practices

1. **Keep Repository Private** - Never make it public with financial data
2. **Use Strong Passwords** - Enable authentication with secure password
3. **Regular Backups** - Download database backups regularly
4. **Monitor Access** - Check Streamlit Cloud analytics for unusual activity
5. **Rotate API Keys** - Change your ExchangeRate API key periodically

## Cost Breakdown

- **Streamlit Cloud**: FREE (1 private app included)
- **GitHub**: FREE (unlimited private repos)
- **ExchangeRate API**: FREE (1,500 requests/month)
- **Total**: $0/month

## Support

- Streamlit Docs: https://docs.streamlit.io
- Streamlit Community: https://discuss.streamlit.io
- GitHub Issues: Create issue in your repository

---

**Estimated Setup Time**: 15-20 minutes

**Mobile Access**: Available immediately after deployment from any device with internet
