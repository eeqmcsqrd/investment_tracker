# Investment Tracker - Quick Start Guide for Mobile Access

Get your investment tracker running on your phone in **15 minutes**.

## Prerequisites
✅ GitHub account  
✅ Investment tracker files on your laptop  
✅ 15 minutes of time  

---

## 🚀 Step 1: Push to GitHub (5 minutes)

Open terminal in your investment tracker folder:

```bash
cd /Users/io/Downloads/investment_tracker

# Create .gitignore (protects sensitive data)
python sync_data_helper.py gitignore

# Initialize git
git init
git add .
git commit -m "Initial commit"

# Create GitHub repo and push
# Go to github.com → New repository → "investment-tracker" → CREATE (make it PRIVATE!)
# Then run:
git remote add origin https://github.com/YOUR_USERNAME/investment-tracker.git
git branch -M main
git push -u origin main
```

---

## 📱 Step 2: Deploy to Streamlit Cloud (5 minutes)

1. Go to **https://share.streamlit.io**
2. Sign in with GitHub
3. Click **"New app"**
4. Fill in:
   - Repository: `YOUR_USERNAME/investment-tracker`
   - Branch: `main`
   - Main file path: `app_db.py` (or `app_db_authenticated.py` for password protection)
5. Click **"Deploy"**

Wait 2-3 minutes for deployment...

---

## 🔑 Step 3: Add Your API Key (2 minutes)

1. In Streamlit Cloud, go to your app settings
2. Click **"Secrets"**
3. Add:
```toml
API_KEY = "your_exchangerate_api_key_here"

# Optional: Add password protection
AUTH_PASSWORD = "your_secure_password"
```
4. Save and reboot app

---

## 📊 Step 4: Upload Your Data (3 minutes)

### Option A: Direct Upload (Easiest)
Your app should have a file uploader. Upload `investment_data.db` directly.

### Option B: Export/Import JSON
```bash
# On your laptop:
python sync_data_helper.py export

# This creates db_snapshot.json
# Upload this file through the app's data import feature
```

---

## ✅ Done! Access Your App

Your app URL will be:
```
https://YOUR_USERNAME-investment-tracker-app-HASH.streamlit.app
```

**Add to iPhone Home Screen:**
1. Open in Safari
2. Tap Share button
3. "Add to Home Screen"
4. Now it looks like a native app!

**Add to Android Home Screen:**
1. Open in Chrome
2. Tap ⋮ menu
3. "Add to Home Screen"
4. Done!

---

## 🔄 Updating Data While Traveling

### Method 1: Enter Directly in App
Use the "Data" tab to add new investment values manually.

### Method 2: Sync from Laptop
```bash
# On laptop (before traveling):
python sync_data_helper.py export

# Upload db_snapshot.json through app
# Or commit to GitHub and redeploy
```

### Method 3: Download Updated Data
Export from the app and download to keep your local copy synced.

---

## 🛡️ Security Tips

- ✅ Keep GitHub repo **PRIVATE**
- ✅ Enable password protection (use `app_db_authenticated.py`)
- ✅ Never commit `.env` or `investment_data.db` to GitHub
- ✅ Use strong passwords
- ✅ Download backups regularly

---

## 🆘 Troubleshooting

**App won't start?**
- Check logs: App settings → Logs
- Verify `requirements.txt` has all dependencies
- Make sure secrets are set correctly

**Missing data?**
- Upload `investment_data.db` or `db_snapshot.json`
- Check database file wasn't corrupted

**Slow performance?**
- First load is always slower (cold start)
- Reduce date range for charts
- Clear browser cache

**Can't access app?**
- Check if app is awake (Streamlit Cloud sleeps after inactivity)
- Verify URL is correct
- Try incognito/private browsing mode

---

## 📞 Need Help?

See detailed guides:
- **DEPLOYMENT_GUIDE.md** - Full deployment instructions
- **README.md** - Complete feature documentation

---

**Total Time: ~15 minutes**  
**Total Cost: $0/month**  
**Mobile Access: ✅ Anywhere with internet**

🎉 Enjoy tracking your investments on the go!
