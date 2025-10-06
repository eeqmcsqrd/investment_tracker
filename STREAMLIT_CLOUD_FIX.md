# Streamlit Cloud Blank Screen Fix

## Issue
When changing date ranges or options in Streamlit Cloud, the app shows a blank screen or missing data.

## Root Causes Identified

### 1. Empty DataFrame After Filtering
When date filters result in no data, some components return early without rendering fallback content.

### 2. Session State Not Initialized
Session state variables may not be properly initialized on Streamlit Cloud.

### 3. Caching Issues
Streamlit's caching might not invalidate properly when date ranges change.

## Quick Fixes

### Fix 1: Add Error Boundaries

Add this at the top of each tab's content in `app_db.py`:

```python
try:
    # Tab content here
    pass
except Exception as e:
    st.error(f"⚠️ Error loading this section: {e}")
    st.info("Try refreshing the page or selecting a different date range.")
    with st.expander("Show technical details"):
        import traceback
        st.code(traceback.format_exc())
```

### Fix 2: Ensure Session State Initialization

In `app_db.py`, ensure these are set BEFORE any tab rendering:

```python
# Initialize session state with defaults
if 'start_date' not in st.session_state or st.session_state.start_date is None:
    st.session_state.start_date = datetime.now().date() - timedelta(days=90)
if 'end_date' not in st.session_state or st.session_state.end_date is None:
    st.session_state.end_date = datetime.now().date()
```

### Fix 3: Add Fallback for Empty Data

In `dashboard_components.py`, replace early returns with informative messages:

```python
if period_df.empty:
    st.warning("📊 No data available for the selected time range")
    st.info("💡 Try:")
    st.markdown("""
    - Selecting a wider date range
    - Choosing different investments
    - Checking that you have data in this period
    """)
    # Show available date range
    if not df.empty:
        st.info(f"Available data: {df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}")
    return  # Still return, but after showing helpful info
```

## Immediate Workaround for Users

### On Streamlit Cloud:

1. **Refresh the page** (F5 or Cmd+R)
2. **Clear cache**: In the menu (☰), click "Clear cache"
3. **Use preset date ranges** instead of custom dates initially
4. **Start with "All Time"** then narrow down

### If Page is Completely Blank:

1. Check the Streamlit Cloud logs for errors
2. Try the "Reboot app" button in Streamlit Cloud dashboard
3. Check if there's a deployment in progress

## Long-term Solutions

### 1. Add Comprehensive Error Handling

Wrap all major sections in try-except blocks with user-friendly error messages.

### 2. Improve Data Validation

Add validation before rendering:

```python
def safe_render(render_func, fallback_message="Data temporarily unavailable"):
    try:
        return render_func()
    except Exception as e:
        st.warning(fallback_message)
        with st.expander("Error details"):
            st.error(str(e))
```

### 3. Add Loading States

Show loading spinners during data processing:

```python
with st.spinner("Loading data..."):
    df_filtered = filter_data(df, start_date, end_date)
```

### 4. Better Session State Management

Use a session state manager:

```python
class SessionManager:
    @staticmethod
    def get_date_range():
        if 'start_date' not in st.session_state:
            st.session_state.start_date = get_default_start()
        if 'end_date' not in st.session_state:
            st.session_state.end_date = get_default_end()
        return st.session_state.start_date, st.session_state.end_date
```

## Testing Checklist

After applying fixes, test:

- [ ] Dashboard loads with default settings
- [ ] Changing date range shows data or appropriate message
- [ ] Each tab works independently
- [ ] Empty data states show helpful messages
- [ ] Errors display user-friendly messages
- [ ] Page never goes completely blank

## Deployment Notes

These fixes are backward compatible and can be deployed without data migration.

Priority: **HIGH**
Estimated time: 30 minutes
Risk: **LOW**
