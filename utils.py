# utils.py
import streamlit as st # type: ignore
import pandas as pd # type: ignore
import time
import re
import base64
import os
import traceback
from datetime import datetime
from io import BytesIO

# Function to encode SVG images for embedding
def svg_to_base64(file_path):
    """
    Encode an SVG file to base64 for embedding in HTML/CSS.
    
    Parameters:
        file_path (str): Path to the SVG file
        
    Returns:
        str: Base64 encoded data URI for the SVG, or None if there was an error
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"SVG file not found: {file_path}")
            print(f"Current working directory: {os.getcwd()}")
            return None
            
        with open(file_path, "rb") as image_file:
            data = image_file.read()
            print(f"Successfully read {len(data)} bytes from {file_path}")
            encoded_string = base64.b64encode(data).decode()
            print(f"Encoded to base64 string of length {len(encoded_string)}")
        return f"data:image/svg+xml;base64,{encoded_string}"
    except Exception as e:
        print(f"Error loading SVG {file_path}: {e}")
        traceback.print_exc()  # Add this for detailed error info
        return None

# Function to get an icon (SVG or emoji fallback)
def get_icon(icon_path, emoji_fallback, width=32, height=32, style=""):
    """
    Get an emoji icon for use in Streamlit.
    
    This function maps path names to appropriate emoji icons without HTML styling,
    as Streamlit often doesn't properly render HTML in certain contexts.
    
    Parameters:
        icon_path (str): Path identifier used to determine which icon to show
        emoji_fallback (str): Default emoji to use if no specific icon is matched
        width (int): Not used directly but kept for compatibility
        height (int): Not used directly but kept for compatibility
        style (str): Not used directly but kept for compatibility
        
    Returns:
        str: An emoji character that represents the requested icon
    """
    try:
        # Determine which emoji to use based on the icon path
        if "search" in icon_path:
            return "🔍"  # Search icon
        elif "sort" in icon_path:
            return "↕️"  # Sort icon
        elif "filter" in icon_path:
            return "🔢"  # Filter icon
        elif "folder" in icon_path:
            return "📁"  # Folder icon
        elif "add" in icon_path:
            return "➕"  # Add icon
        elif "refresh" in icon_path:
            return "🔄"  # Refresh icon
        elif "download" in icon_path or "export" in icon_path:
            return "📥"  # Download icon
        elif "save" in icon_path:
            return "💾"  # Save icon
        elif "import" in icon_path:
            return "📤"  # Import icon
        elif "info" in icon_path:
            return "ℹ️"  # Info icon
        elif "success" in icon_path:
            return "✅"  # Success icon
        elif "warning" in icon_path:
            return "⚠️"  # Warning icon
        elif "error" in icon_path:
            return "❌"  # Error icon
        elif "dashboard" in icon_path:
            return "📊"  # Dashboard icon
        elif "performance" in icon_path:
            return "📈"  # Performance icon
        elif "data" in icon_path:
            return "📋"  # Data icon
        elif "settings" in icon_path:
            return "⚙️"  # Settings icon
        else:
            # Fall back to the provided emoji fallback
            return emoji_fallback
    
    except Exception as e:
        print(f"Error processing icon {icon_path}: {e}")
        # Return fallback emoji in case of any errors
        return emoji_fallback

# Function to create a progress animation that was previously missing
def create_progress_animation(duration=0.01):
    """
    Creates a simple progress animation that fills up to 100%.
    
    Parameters:
        duration (float): Time delay between progress updates in seconds
        
    Returns:
        None
    """
    progress_bar = st.progress(0)
    for i in range(101):
        # Update progress bar
        progress_bar.progress(i)
        time.sleep(duration)  # Small delay for animation effect
    progress_bar.empty()  # Clear the progress bar when done

# Generic function to handle animated processes
def animated_process(process_func, spinner_message, duration=0.01):
    """
    Execute a function with a progress animation to give visual feedback.
    
    Parameters:
        process_func (callable): The function to execute
        spinner_message (str): Message to display while processing
        duration (float): Time delay between progress updates in seconds
        
    Returns:
        The return value of the process_func
    """
    with st.spinner(spinner_message):
        progress_bar = st.progress(0)
        for i in range(101):
            progress_bar.progress(i)
            time.sleep(duration)
            
        # Execute the actual process function
        result = process_func()
        
    return result

# Function to create date picker with "Use today's date" checkbox
def create_date_picker(use_today_key, date_picker_key):
    """
    Create a date picker with an option to use today's date.
    
    Parameters:
        use_today_key (str): Key for the "Use today's date" checkbox
        date_picker_key (str): Key for the date picker
        
    Returns:
        datetime.date: The selected date
    """
    col1, col2 = st.columns(2)
    
    with col1:
        use_today = st.checkbox("Use today's date", value=True, key=use_today_key)
    
    with col2:
        if use_today:
            entry_date = datetime.now().date()
            st.info(f"Using: {entry_date.strftime('%Y-%m-%d')}")
        else:
            entry_date = st.date_input(
                "Entry Date", 
                value=datetime.now(),
                key=date_picker_key
            )
    
    return entry_date

# Function to apply common styling to charts
def apply_chart_styling(fig, height=400, x_title="Date", y_title="Value", 
                        margin=None, hovermode="x unified"):
    """
    Apply consistent styling to Plotly charts.
    
    Parameters:
        fig (plotly.graph_objects.Figure): The figure to style
        height (int): Chart height in pixels
        x_title (str): X-axis title
        y_title (str): Y-axis title
        margin (dict): Chart margins
        hovermode (str): Hover mode for the chart
        
    Returns:
        plotly.graph_objects.Figure: The styled figure
    """
    if margin is None:
        margin = dict(l=20, r=20, t=30, b=20)
        
    fig.update_layout(
        height=height,
        xaxis_title=x_title,
        yaxis_title=y_title,
        margin=margin,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(
            gridcolor='rgba(255,255,255,0.1)',
            zerolinecolor='rgba(255,255,255,0.2)'
        ),
        yaxis=dict(
            gridcolor='rgba(255,255,255,0.1)',
            zerolinecolor='rgba(255,255,255,0.2)'
        ),
        hovermode=hovermode
    )
    
    return fig

# Function to create export buttons based on format and data
def create_export_buttons(export_df, export_format, filename_prefix="investment_data", button_label=None, icon=None):
    """
    Create download buttons for exporting data in different formats.
    
    Parameters:
        export_df (pandas.DataFrame): The data to export
        export_format (str): Format to export ("CSV", "Excel", or "JSON")
        filename_prefix (str): Prefix for the exported filename
        button_label (str): Label for the download button
        icon (str): Icon to display on the button
        
    Returns:
        None
    """
    if button_label is None:
        button_label = "Download Data"
    
    if icon:
        button_label = f"{icon} {button_label}"
    
    if export_format == "CSV":
        csv = export_df.to_csv(index=False)
        st.download_button(
            label=button_label,
            data=csv,
            file_name=f"{filename_prefix}.csv",
            mime="text/csv",
            use_container_width=True
        )
    elif export_format == "Excel":
        # For Excel, we need to use BytesIO
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            export_df.to_excel(writer, sheet_name='Investment Data', index=False)
            
            # Auto-adjust column width
            worksheet = writer.sheets['Investment Data']
            for i, col in enumerate(export_df.columns):
                column_len = max(export_df[col].astype(str).str.len().max(), len(col) + 2)
                worksheet.set_column(i, i, column_len)
        
        excel_data = buffer.getvalue()
        
        st.download_button(
            label=button_label,
            data=excel_data,
            file_name=f"{filename_prefix}.xlsx",
            mime="application/vnd.ms-excel",
            use_container_width=True
        )
    else:  # JSON
        json_str = export_df.to_json(orient='records', date_format='iso')
        st.download_button(
            label=button_label,
            data=json_str,
            file_name=f"{filename_prefix}.json",
            mime="application/json",
            use_container_width=True
        )

# Function to get date range parameters based on preset selections
def get_date_range(preset_range, latest_date, earliest_date):
    """
    Calculate date range based on preset selections.
    
    Parameters:
        preset_range (str): Preset range identifier
        latest_date (datetime.date): Latest available date
        earliest_date (datetime.date): Earliest available date
        
    Returns:
        tuple: (start_date, end_date) for the selected range
    """
    now = datetime.now().date()
    
    if preset_range == "1 Month":
        start_date = (now - pd.Timedelta(days=30))
        end_date = now
    elif preset_range == "3 Months":
        start_date = (now - pd.Timedelta(days=90))
        end_date = now
    elif preset_range == "6 Months":
        start_date = (now - pd.Timedelta(days=180))
        end_date = now
    elif preset_range == "1 Year":
        start_date = (now - pd.Timedelta(days=365))
        end_date = now
    elif preset_range == "YTD":
        start_date = datetime(now.year, 1, 1).date()
        end_date = now
    else:  # All Time
        start_date = earliest_date
        end_date = latest_date
    
    return start_date, end_date

# Function to filter dataframe by date and investments
def filter_dataframe(df, start_date, end_date, investment_filter="All"):
    """
    Filter a DataFrame by date range and investment name.
    
    Parameters:
        df (pandas.DataFrame): DataFrame to filter
        start_date (datetime.date): Start date for filtering
        end_date (datetime.date): End date for filtering
        investment_filter (str or list): Investment(s) to include, or "All"
        
    Returns:
        pandas.DataFrame: Filtered DataFrame
    """
    filtered_df = df.copy()
    
    # Date filter
    filtered_df = filtered_df[
        (filtered_df['Date'] >= pd.Timestamp(start_date)) &
        (filtered_df['Date'] <= pd.Timestamp(end_date))
    ]
    
    # Investment filter
    if investment_filter != "All" and not isinstance(investment_filter, list) or \
       isinstance(investment_filter, list) and "All" not in investment_filter:
        filtered_df = filtered_df[filtered_df['Investment'].isin(investment_filter)]
    
    return filtered_df

# Function to create a date filter UI component with preset options
def create_date_filter_ui(earliest_date, latest_date, filter_type_key="date_filter_type", 
                          preset_key="date_preset", start_key="data_start", end_key="data_end",
                          specific_date_type_key="specific_date_type", specific_date_key="specific_date"):
    """
    Create a UI component for date filtering with various options.
    
    Parameters:
        earliest_date (datetime.date): Earliest available date
        latest_date (datetime.date): Latest available date
        filter_type_key (str): Key for filter type radio buttons
        preset_key (str): Key for preset range selectbox
        start_key (str): Key for start date input
        end_key (str): Key for end date input
        specific_date_type_key (str): Key for specific date type radio buttons
        specific_date_key (str): Key for specific date input
        
    Returns:
        tuple: (start_date, end_date) based on user selection
    """
    date_filter_type = st.radio(
        "Filter Type",
        ["Range", "Specific Date"],
        horizontal=True,
        key=filter_type_key
    )
    
    if date_filter_type == "Range":
        # Date range selection with presets
        date_preset = st.selectbox(
            "Preset Ranges",
            ["Custom", "Last 30 Days", "Last 90 Days", "Last 180 Days", "This Year", "Last Year", "All Time"],
            key=preset_key
        )
        
        if date_preset == "Custom":
            # Custom date range
            data_cols = st.columns([1, 1, 2])
            with data_cols[0]:
                start_date = st.date_input(
                    "From", 
                    value=earliest_date,
                    min_value=earliest_date,
                    max_value=latest_date,
                    key=start_key
                )
            with data_cols[1]:
                end_date = st.date_input(
                    "To", 
                    value=latest_date,
                    min_value=earliest_date,
                    max_value=latest_date,
                    key=end_key
                )
        else:
            # Calculate preset ranges
            if date_preset == "Last 30 Days":
                start_date = latest_date - pd.Timedelta(days=30)
                end_date = latest_date
            elif date_preset == "Last 90 Days":
                start_date = latest_date - pd.Timedelta(days=90)
                end_date = latest_date
            elif date_preset == "Last 180 Days":
                start_date = latest_date - pd.Timedelta(days=180)
                end_date = latest_date
            elif date_preset == "This Year":
                start_date = datetime(latest_date.year, 1, 1).date()
                end_date = latest_date
            elif date_preset == "Last Year":
                start_date = datetime(latest_date.year - 1, 1, 1).date()
                end_date = datetime(latest_date.year - 1, 12, 31).date()
            else:  # All Time
                start_date = earliest_date
                end_date = latest_date
            
            st.info(f"ℹ️ Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    else:
        # Specific date selection
        data_cols = st.columns([1, 3])
        with data_cols[0]:
            specific_date_type = st.radio(
                "Date Selection",
                ["Specific Date", "Latest Available"],
                key=specific_date_type_key
            )
        
        with data_cols[1]:
            if specific_date_type == "Specific Date":
                specific_date = st.date_input(
                    "Select Date",
                    value=latest_date,
                    min_value=earliest_date,
                    max_value=latest_date,
                    key=specific_date_key
                )
                start_date = end_date = specific_date
            else:
                start_date = end_date = latest_date
                st.info(f"ℹ️ Using latest date: {latest_date.strftime('%Y-%m-%d')}")
    
    return start_date, end_date

def update_investment_config(investment_name, currency, category, add_to_tracked=False):
    """
    Update config.py file to add a new investment.
    
    Parameters:
        investment_name (str): Name of the new investment
        currency (str): Currency used by the investment
        category (str): Category of the investment
        add_to_tracked (bool): Whether to add the investment to tracked investments
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        import re
        
        # Read the current config file
        with open('config.py', 'r') as file:
            config_content = file.read()
        
        # Ensure investment name is properly formatted as string
        investment_name = str(investment_name)
        
        # Process the investment name to handle quotes correctly
        # Avoiding the complexity entirely
        if '"' in investment_name:
            # If there are double quotes in the name, use single quotes around it
            investment_str = "'" + investment_name + "'"
        else:
            # Otherwise use double quotes
            investment_str = '"' + investment_name + '"'
            
        # Update INVESTMENT_ACCOUNTS dictionary
        accounts_regex = r'INVESTMENT_ACCOUNTS\s*=\s*\{str\(k\):\s*v\s*for\s*k,\s*v\s*in\s*\{([^}]*)\}\.items\(\)\}'
        accounts_match = re.search(accounts_regex, config_content)
        
        if accounts_match:
            accounts_content = accounts_match.group(1)
            # Add the new investment at the end before the comment line
            if "# Add any additional accounts here" in accounts_content:
                new_accounts_content = accounts_content.replace(
                    "# Add any additional accounts here",
                    f'{investment_str}: "{currency}",\n    # Add any additional accounts here'
                )
            else:
                new_accounts_content = accounts_content + f',\n    {investment_str}: "{currency}"'
                
            config_content = config_content.replace(accounts_match.group(1), new_accounts_content)
        
        # Update INVESTMENT_CATEGORIES dictionary
        categories_regex = r'INVESTMENT_CATEGORIES\s*=\s*\{str\(k\):\s*v\s*for\s*k,\s*v\s*in\s*\{([^}]*)\}\.items\(\)\}'
        categories_match = re.search(categories_regex, config_content)
        
        if categories_match:
            categories_content = categories_match.group(1)
            # Add the new category at the end before the comment line
            if "# Add any additional categories here" in categories_content:
                new_categories_content = categories_content.replace(
                    "# Add any additional categories here",
                    f'{investment_str}: "{category}",\n    # Add any additional categories here'
                )
            else:
                new_categories_content = categories_content + f',\n    {investment_str}: "{category}"'
                
            config_content = config_content.replace(categories_match.group(1), new_categories_content)
        
        # Update TRACKED_INVESTMENTS list if requested
        if add_to_tracked:
            tracked_regex = r'TRACKED_INVESTMENTS\s*=\s*\[(.*?)\]'
            tracked_match = re.search(tracked_regex, config_content, re.DOTALL)
            
            if tracked_match:
                tracked_content = tracked_match.group(1)
                # Check if the list is empty
                if tracked_content.strip() == '':
                    new_tracked_content = f"'{investment_name}'"
                else:
                    new_tracked_content = tracked_content + f",\n    '{investment_name}'"
                    
                config_content = config_content.replace(tracked_match.group(1), new_tracked_content)
        
        # Write the updated content back to the file
        with open('config.py', 'w') as file:
            file.write(config_content)
            
        # Also update the in-memory dictionaries to make the change immediate
        from config import INVESTMENT_ACCOUNTS, INVESTMENT_CATEGORIES, TRACKED_INVESTMENTS
        import importlib
        
        # Update the dictionaries
        INVESTMENT_ACCOUNTS[investment_name] = currency
        INVESTMENT_CATEGORIES[investment_name] = category
        
        if add_to_tracked and investment_name not in TRACKED_INVESTMENTS:
            TRACKED_INVESTMENTS.append(investment_name)
        
        # Force reload of the config module to update all references
        import config
        importlib.reload(config)
        
        return True
        
    except Exception as e:
        print(f"Error updating config file: {e}")
        import traceback
        traceback.print_exc()
        return False