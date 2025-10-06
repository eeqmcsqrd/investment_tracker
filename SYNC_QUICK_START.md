# Auto-Sync Quick Start ⚡

## What You Can Do Now

Update investments on your laptop → **They automatically appear in Streamlit Cloud!**

---

## 3-Minute Setup

### Step 1: Enable Auto-Sync (in the app)

```
1. Run: streamlit run app_db.py
2. Go to: Settings tab → Auto-Sync sub-tab
3. Toggle: "Enable Auto-Sync" to ON
4. Select: "Immediate" mode
5. Click: "Save Settings"
```

### Step 2: Test It

```
1. Add a test investment entry
2. Go to Settings → Auto-Sync
3. Click "Sync Now"
4. Check your GitHub repo - new commit!
5. Wait 1-2 minutes
6. Check Streamlit Cloud - data updated!
```

### Step 3: Done! 🎉

Now whenever you update investments on your laptop:
- Changes sync to GitHub automatically
- Streamlit Cloud updates within 2 minutes
- View on any device (phone, tablet, etc.)

---

## Daily Usage

### Quick Sync While Traveling

```bash
# Update investments on laptop
# Then in the app:
Settings → Auto-Sync → Click "Sync Now"

# Check Streamlit Cloud on phone (1-2 min later)
# ✅ Your changes are there!
```

### Automatic Sync (Set It and Forget It)

```bash
# One-time setup:
Settings → Auto-Sync
  ✅ Enable Auto-Sync: ON
  ✅ Sync Mode: Immediate
  ✅ Save Settings

# Now just use the app normally!
# Every change auto-syncs to cloud
```

---

## Command Line (Optional)

### Manual Sync from Terminal

```bash
cd /Users/io/Downloads/investment_tracker
python auto_sync.py --once
```

### Background Daemon

```bash
# Monitors continuously
python auto_sync.py --daemon

# Press Ctrl+C to stop
```

---

## Troubleshooting

### "Sync Failed"

**Check internet connection:**
```bash
ping github.com
```

**Check git authentication:**
```bash
git push origin main
# If it asks for password, enter it once
# It will be saved for future syncs
```

### "Changes Not in Streamlit Cloud"

**Wait 2 minutes** - Streamlit Cloud rebuilds automatically

**Or force rebuild:**
1. Go to Streamlit Cloud dashboard
2. Click "Reboot app"

---

## What Gets Synced

✅ **investment_data.db** - Your database
✅ **db_snapshot.json** - JSON export for cloud

❌ **Not synced** (for security):
- `.env` files (secrets)
- `exchange_rates_cache.json` (temporary)
- `__pycache__` (Python cache)

---

## Sync Status

### Check in App

```
Settings → Auto-Sync → Sync Status section

Shows:
- Database Hash: Current state
- Last Sync Hash: Last synced state
- Status: ✅ Synced / ⚠️ Pending
```

### Check on GitHub

```
https://github.com/eeqmcsqrd/investment_tracker/commits/main

Look for commits like:
"Auto-sync: Update investment data"
```

---

## Tips & Tricks

### Batch Updates

```
1. Disable Auto-Sync
2. Make 10 changes
3. Click "Sync Now" once
4. All 10 changes sync together
```

### Mobile Viewing

```
1. Update on laptop (auto-syncs)
2. Open Streamlit Cloud on phone
3. Wait 1-2 minutes
4. Refresh page
5. ✅ See your updates!
```

### Check Before Closing Laptop

```
Before bed:
1. Settings → Auto-Sync
2. Check status shows "✅ Synced"
3. If "⚠️ Pending", click "Sync Now"
4. Close laptop
```

---

## Need More Help?

📚 **Full Documentation**: See [AUTO_SYNC_GUIDE.md](AUTO_SYNC_GUIDE.md)

🔧 **Support**: Check sync status in Settings → Auto-Sync

✅ **It Just Works**: Once enabled, sync happens automatically!

---

## Summary

| Task | How |
|------|-----|
| **Enable sync** | Settings → Auto-Sync → Toggle ON |
| **Sync now** | Settings → Auto-Sync → "Sync Now" |
| **Check status** | Settings → Auto-Sync → Sync Status |
| **View changes** | Streamlit Cloud (wait 1-2 min) |

**That's it!** Your investment data now syncs automatically between laptop and cloud. 🎉

---

**Version**: 1.0
**Status**: ✅ Ready to use
**Time to set up**: < 3 minutes
