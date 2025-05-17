# CHUNK 1: Module Imports and Dashboard Header Function
import streamlit as st # type: ignore
import pandas as pd # type: ignore
import plotly.express as px # type: ignore
import plotly.graph_objects as go # type: ignore
from datetime import datetime, timedelta
import numpy as np # type: ignore
from math import floor, ceil

def create_dashboard_header():
    """Create an enhanced dashboard header with metrics row"""
    st.markdown("""
    <div class="dashboard-header">
        <h1>Portfolio Dashboard</h1>
        <p class="subtitle">Track your investment performance across accounts and categories</p>
    </div>
    """, unsafe_allow_html=True)
# CHUNK 2: Themed Metrics Function (First Part)
def create_themed_metrics(latest_df, df, latest_date):
    """Create enhanced thematic metrics with dynamic colors based on performance"""
    if not latest_df.empty:
        # Calculate total portfolio value
        total_usd = latest_df['ValueUSD'].sum()
        
        # Create a 4-column layout for key metrics
        metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
        
        # Add themed metric cards
        with metrics_col1:
            st.markdown("""
            <div class="metric-card total-value">
                <div class="metric-icon">💰</div>
                <div class="metric-content">
                    <h3>Total Portfolio Value</h3>
                    <p class="metric-value">${:,.2f} USD</p>
                </div>
            </div>
            """.format(total_usd), unsafe_allow_html=True)
        
        # Calculate 1 month change with improved error handling and theming
        try:
            one_month_ago = latest_date - timedelta(days=30)
            closest_date = df[df['Date'] <= one_month_ago]['Date'].max()
            
            if pd.notna(closest_date):
                month_df = df[df['Date'] == closest_date]
                month_total = month_df['ValueUSD'].sum()
                month_change = total_usd - month_total
                month_percent = (month_change / month_total) * 100 if month_total > 0 else 0
                
                # Determine color theme based on performance
                theme_class = "positive-change" if month_change >= 0 else "negative-change"
                icon = "📈" if month_change >= 0 else "📉"
                
                with metrics_col2:
                    st.markdown(f"""
                    <div class="metric-card {theme_class}">
                        <div class="metric-icon">{icon}</div>
                        <div class="metric-content">
                            <h3>1 Month Change</h3>
                            <p class="metric-value">${month_change:,.2f} ({month_percent:.2f}%)</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                with metrics_col2:
                    st.markdown("""
                    <div class="metric-card neutral">
                        <div class="metric-icon">🔄</div>
                        <div class="metric-content">
                            <h3>1 Month Change</h3>
                            <p class="metric-value">N/A</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        except Exception:
            with metrics_col2:
                st.markdown("""
                <div class="metric-card neutral">
                    <div class="metric-icon">🔄</div>
                    <div class="metric-content">
                        <h3>1 Month Change</h3>
                        <p class="metric-value">N/A</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
# CHUNK 3: Themed Metrics Function (Second Part)
        # Calculate 3 month change with themed UI
        try:
            three_months_ago = latest_date - timedelta(days=90)
            closest_date = df[df['Date'] <= three_months_ago]['Date'].max()
            
            if pd.notna(closest_date):
                quarter_df = df[df['Date'] == closest_date]
                quarter_total = quarter_df['ValueUSD'].sum()
                quarter_change = total_usd - quarter_total
                quarter_percent = (quarter_change / quarter_total) * 100 if quarter_total > 0 else 0
                
                # Determine color theme
                theme_class = "positive-change" if quarter_change >= 0 else "negative-change"
                icon = "📈" if quarter_change >= 0 else "📉"
                
                with metrics_col3:
                    st.markdown(f"""
                    <div class="metric-card {theme_class}">
                        <div class="metric-icon">{icon}</div>
                        <div class="metric-content">
                            <h3>3 Month Change</h3>
                            <p class="metric-value">${quarter_change:,.2f} ({quarter_percent:.2f}%)</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                with metrics_col3:
                    st.markdown("""
                    <div class="metric-card neutral">
                        <div class="metric-icon">🔄</div>
                        <div class="metric-content">
                            <h3>3 Month Change</h3>
                            <p class="metric-value">N/A</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        except Exception:
            with metrics_col3:
                st.markdown("""
                <div class="metric-card neutral">
                    <div class="metric-icon">🔄</div>
                    <div class="metric-content">
                        <h3>3 Month Change</h3>
                        <p class="metric-value">N/A</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
# CHUNK 4: Themed Metrics Function (Third Part)
        # Calculate YTD change with themed UI
        try:
            start_of_year = datetime(latest_date.year, 1, 1).date()
            closest_date = df[df['Date'] >= start_of_year]['Date'].min()
            
            if pd.notna(closest_date):
                ytd_df = df[df['Date'] == closest_date]
                ytd_total = ytd_df['ValueUSD'].sum()
                ytd_change = total_usd - ytd_total
                ytd_percent = (ytd_change / ytd_total) * 100 if ytd_total > 0 else 0
                
                # Determine color theme
                theme_class = "positive-change" if ytd_change >= 0 else "negative-change"
                icon = "📈" if ytd_change >= 0 else "📉"
                
                with metrics_col4:
                    st.markdown(f"""
                    <div class="metric-card {theme_class}">
                        <div class="metric-icon">{icon}</div>
                        <div class="metric-content">
                            <h3>YTD Change</h3>
                            <p class="metric-value">${ytd_change:,.2f} ({ytd_percent:.2f}%)</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                with metrics_col4:
                    st.markdown("""
                    <div class="metric-card neutral">
                        <div class="metric-icon">🔄</div>
                        <div class="metric-content">
                            <h3>YTD Change</h3>
                            <p class="metric-value">N/A</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        except Exception:
            with metrics_col4:
                st.markdown("""
                <div class="metric-card neutral">
                    <div class="metric-icon">🔄</div>
                    <div class="metric-content">
                        <h3>YTD Change</h3>
                        <p class="metric-value">N/A</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No data available. Please add investment entries.")
# CHUNK 5: Enhanced Asset Allocation Function (First Part)
def create_enhanced_asset_allocation(latest_df, INVESTMENT_CATEGORIES):
    """Create an enhanced asset allocation visualization with thematic colors"""
    if not latest_df.empty:
        st.subheader("Asset Allocation")
        
        # Group by investment and calculate percentages
        allocation = latest_df.groupby('Investment')['ValueUSD'].sum().reset_index()
        allocation['Percentage'] = (allocation['ValueUSD'] / allocation['ValueUSD'].sum() * 100).round(2)
        
        # Add category information
        allocation['Category'] = allocation['Investment'].map(INVESTMENT_CATEGORIES)
        
        # Create tabs for different visualization types
        allocation_tabs = st.tabs(["Pie Chart", "Treemap", "Bar Chart"])
        
        # Define a consistent color palette for categories
        category_colors = {
            "Stocks": "#4361ee",
            "Bonds": "#3a0ca3",
            "ETFs": "#7209b7",
            "Crypto": "#f72585",
            "Real Estate": "#4cc9f0",
            "Cash": "#4ade80",
            "Commodities": "#fb8500",
            "Other": "#8d99ae"
        }
        
        # Fill in any missing categories with default colors
        for category in allocation['Category'].unique():
            if category not in category_colors:
                category_colors[category] = "#8d99ae"  # Default gray
        
        # Create color mapping
        color_discrete_map = {}
        for idx, row in allocation.iterrows():
            category = row['Category']
            investment = row['Investment']
            # Assign color based on category with slight variations for different investments
            base_color = category_colors.get(category, "#8d99ae")
            # Convert hex to RGB to adjust brightness
            r = int(base_color[1:3], 16)
            g = int(base_color[3:5], 16)
            b = int(base_color[5:7], 16)
            # Adjust brightness slightly (±10%) based on investment name hash
            brightness_adj = (hash(investment) % 20) - 10  # -10% to +10%
            r = max(0, min(255, r + int(r * brightness_adj / 100)))
            g = max(0, min(255, g + int(g * brightness_adj / 100)))
            b = max(0, min(255, b + int(b * brightness_adj / 100)))
            # Convert back to hex
            color_discrete_map[investment] = f"#{r:02x}{g:02x}{b:02x}"
# CHUNK 6: Enhanced Asset Allocation Function (Second Part)
        # Allow filtering by threshold percentage
        min_pct = st.slider(
            "Minimum percentage to display (smaller holdings grouped as 'Other')", 
            min_value=0.0, 
            max_value=10.0, 
            value=1.0,
            step=0.5,
            key="pie_threshold"
        )
        
        # Group small investments as "Other"
        filtered_allocation = allocation.copy()
        if min_pct > 0:
            small_investments = filtered_allocation[filtered_allocation['Percentage'] < min_pct]
            if not small_investments.empty:
                other_row = {
                    'Investment': 'Other Small Holdings',
                    'ValueUSD': small_investments['ValueUSD'].sum(),
                    'Percentage': small_investments['Percentage'].sum(),
                    'Category': 'Other'
                }
                filtered_allocation = filtered_allocation[filtered_allocation['Percentage'] >= min_pct]
                filtered_allocation = pd.concat([filtered_allocation, pd.DataFrame([other_row])], ignore_index=True)
                # Add color for "Other Small Holdings"
                color_discrete_map['Other Small Holdings'] = "#adb5bd"
        
        # Pie Chart
        with allocation_tabs[0]:
            # Add checkbox to control pie explosion
            exploded_view = st.checkbox("Show exploded view", value=False, key="exploded_pie")
            
            # Create improved pie chart
            fig = px.pie(
                filtered_allocation, 
                values='ValueUSD', 
                names='Investment',
                hover_data=['Percentage'],
                labels={'ValueUSD': 'Value (USD)'},
                title='Asset Allocation by Investment',
                color='Investment',
                color_discrete_map=color_discrete_map
            )
            
            # Enhanced styling for interactive pie chart
            fig.update_traces(
                textposition='inside', 
                textinfo='percent+label',
                textfont_size=12,
                pull=[0.15 if exploded_view else 0.05] * len(filtered_allocation),
                marker=dict(line=dict(color='#1e1e2e', width=1)),
                hovertemplate='<b>%{label}</b><br>Value: $%{value:,.2f}<br>Percentage: %{customdata[0]:.2f}%<extra></extra>'
            )
            
            # Apply styling
            fig.update_layout(
                height=500,
                margin=dict(l=20, r=20, t=30, b=100),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.30,
                    xanchor="center",
                    x=0.5,
                    bgcolor="rgba(0,0,0,0.1)",
                    bordercolor="rgba(255,255,255,0.2)",
                    borderwidth=1
                ),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key="asset_allocation_pie")
# CHUNK 7: Enhanced Asset Allocation Function (Third Part - Treemap and Bar Chart)
        # Treemap
        with allocation_tabs[1]:
            # Create a hierarchical dataset for the treemap
            treemap_data = filtered_allocation.copy()
            
            # Create treemap based on category and investment hierarchy
            fig = px.treemap(
                treemap_data,
                path=['Category', 'Investment'],
                values='ValueUSD',
                color='Investment',
                color_discrete_map=color_discrete_map,
                hover_data=['Percentage'],
                title='Asset Allocation by Category and Investment'
            )
            
            # Enhanced styling
            fig.update_traces(
                textinfo='label+percent parent+value',
                hovertemplate='<b>%{label}</b><br>Value: $%{value:,.2f}<br>Percentage: %{customdata[0]:.2f}%<extra></extra>'
            )
            
            # Apply styling
            fig.update_layout(
                height=500,
                margin=dict(l=20, r=20, t=30, b=20),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key="asset_allocation_treemap")
        
        # Bar Chart
        with allocation_tabs[2]:
            # Create horizontal bar chart
            fig = px.bar(
                filtered_allocation.sort_values('ValueUSD', ascending=True),
                y='Investment',
                x='ValueUSD',
                color='Investment',
                color_discrete_map=color_discrete_map,
                text='Percentage',
                orientation='h',
                title='Asset Allocation by Investment',
                labels={'ValueUSD': 'Value (USD)', 'Investment': 'Investment'}
            )
            
            # Enhanced styling
            fig.update_traces(
                texttemplate='%{text:.1f}%',
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>Value: $%{x:,.2f}<br>Percentage: %{text:.1f}%<extra></extra>'
            )
            
            # Apply styling
            fig.update_layout(
                height=500,
                margin=dict(l=20, r=40, t=30, b=20),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title='Value (USD)',
                yaxis_title='',
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key="category_breakdown_hbar")
    else:
        st.info("No data available. Please add investment entries.")
# CHUNK 8: Enhanced Currency Breakdown Function (First Part)
def create_enhanced_currency_breakdown(latest_df):
    """Create enhanced currency breakdown visualization with thematic colors"""
    if not latest_df.empty:
        st.subheader("Currency Breakdown")
        
        # Group by currency
        currency_breakdown = latest_df.groupby('Currency')['ValueUSD'].sum().reset_index()
        currency_breakdown['Percentage'] = (currency_breakdown['ValueUSD'] / currency_breakdown['ValueUSD'].sum() * 100).round(2)
        
        # Create tabs for different visualization types
        currency_tabs = st.tabs(["Bar Chart", "Pie Chart", "Treemap"])
        
        # Define a consistent color palette for currencies
        currency_colors = {
            "USD": "#118ab2",
            "EUR": "#06d6a0",
            "GBP": "#073b4c",
            "CAD": "#ef476f",
            "JPY": "#ffd166",
            "AUD": "#7209b7",
            "CHF": "#4cc9f0"
        }
        
        # Fill in any missing currencies with default colors
        for currency in currency_breakdown['Currency'].unique():
            if currency not in currency_colors:
                currency_colors[currency] = "#8d99ae"  # Default gray
        
        # Bar Chart
        with currency_tabs[0]:
            fig = px.bar(
                currency_breakdown.sort_values('ValueUSD', ascending=False),
                x='Currency',
                y='ValueUSD',
                text='Percentage',
                color='Currency',
                color_discrete_map=currency_colors,
                labels={'ValueUSD': 'Value (USD)', 'Currency': 'Currency'},
                title='Portfolio Value by Currency'
            )
            
            fig.update_traces(
                texttemplate='%{text:.1f}%', 
                textposition='outside',
                marker_line_color='rgba(255,255,255,0.2)',
                marker_line_width=1,
                hovertemplate='<b>%{x}</b><br>Value: $%{y:,.2f}<br>Percentage: %{text:.1f}%<extra></extra>'
            )
            
            # Apply styling
            fig.update_layout(
                height=450,
                margin=dict(l=20, r=20, t=30, b=20),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title='Currency',
                yaxis_title='Value (USD)',
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key="currency_breakdown_bar")
# CHUNK 9: Enhanced Currency Breakdown Function (Second Part)
        # Pie Chart
        with currency_tabs[1]:
            fig = px.pie(
                currency_breakdown,
                values='ValueUSD',
                names='Currency',
                hover_data=['Percentage'],
                color='Currency',
                color_discrete_map=currency_colors,
                title='Portfolio Distribution by Currency'
            )
            
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                marker=dict(line=dict(color='#1e1e2e', width=1)),
                hovertemplate='<b>%{label}</b><br>Value: $%{value:,.2f}<br>Percentage: %{customdata[0]:.1f}%<extra></extra>'
            )
            
            # Apply styling
            fig.update_layout(
                height=450,
                margin=dict(l=20, r=20, t=30, b=20),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key="currency_breakdown_pie")
        
        # Treemap
        with currency_tabs[2]:
            fig = px.treemap(
                currency_breakdown,
                path=['Currency'],
                values='ValueUSD',
                color='Currency',
                color_discrete_map=currency_colors,
                hover_data=['Percentage'],
                title='Portfolio Distribution by Currency'
            )
            
            fig.update_traces(
                textinfo='label+value+percent root',
                hovertemplate='<b>%{label}</b><br>Value: $%{value:,.2f}<br>Percentage: %{customdata[0]:.1f}%<extra></extra>'
            )
            
            # Apply styling
            fig.update_layout(
                height=450,
                margin=dict(l=20, r=20, t=30, b=20),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key="currency_breakdown_treemap")
    else:
        st.info("No data available. Please add investment entries.")
# CHUNK 10: Enhanced Category Breakdown Function (First Part)
def create_enhanced_category_breakdown(latest_df, INVESTMENT_CATEGORIES):
    """Create enhanced category breakdown visualization with thematic colors"""
    if not latest_df.empty:
        st.subheader("Category Breakdown")
        
        # Group by category
        category_data = latest_df.copy()
        category_data['Category'] = category_data['Investment'].map(INVESTMENT_CATEGORIES)
        category_breakdown = category_data.groupby('Category')['ValueUSD'].sum().reset_index()
        category_breakdown['Percentage'] = (category_breakdown['ValueUSD'] / category_breakdown['ValueUSD'].sum() * 100).round(2)
        
        # Define a consistent color palette for categories
        category_colors = {
            "Stocks": "#4361ee",
            "Bonds": "#3a0ca3",
            "ETFs": "#7209b7",
            "Crypto": "#f72585",
            "Real Estate": "#4cc9f0",
            "Cash": "#4ade80",
            "Commodities": "#fb8500",
            "Other": "#8d99ae"
        }
        
        # Fill in any missing categories with default colors
        for category in category_breakdown['Category'].unique():
            if category not in category_colors:
                category_colors[category] = "#8d99ae"  # Default gray
        
        # Create tabs for different visualization types
        category_tabs = st.tabs(["Horizontal Bar", "Sunburst", "Treemap", "Radar"])
        
        # Horizontal Bar
        with category_tabs[0]:
            fig = px.bar(
                category_breakdown.sort_values('ValueUSD', ascending=True),
                y='Category',
                x='ValueUSD',
                text='Percentage',
                color='Category',
                color_discrete_map=category_colors,
                orientation='h',
                labels={'ValueUSD': 'Value (USD)', 'Category': 'Category'},
                title='Portfolio Value by Category'
            )
            
            fig.update_traces(
                texttemplate='%{text:.1f}%', 
                textposition='inside',
                marker_line_color='rgba(255,255,255,0.2)',
                marker_line_width=1,
                hovertemplate='<b>%{y}</b><br>Value: $%{x:,.2f}<br>Percentage: %{text:.1f}%<extra></extra>'
            )
            
            # Apply styling
            fig.update_layout(
                height=350,
                margin=dict(l=20, r=20, t=30, b=20),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title='Value (USD)',
                yaxis_title='',
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
# CHUNK 11: Enhanced Category Breakdown Function (Second Part)
        # Sunburst
        with category_tabs[1]:
            # Create a more detailed dataset for the sunburst chart
            sunburst_data = latest_df.copy()
            sunburst_data['Category'] = sunburst_data['Investment'].map(INVESTMENT_CATEGORIES)
            
            # Create sunburst chart for category > investment hierarchy
            fig = px.sunburst(
                sunburst_data,
                path=['Category', 'Investment'],
                values='ValueUSD',
                color='Category',
                color_discrete_map=category_colors,
                hover_data=['Currency', 'Value'],
                title='Portfolio Hierarchy by Category and Investment'
            )
            
            fig.update_traces(
                textinfo='label+percent entry',
                hovertemplate='<b>%{label}</b><br>Value: $%{value:,.2f}<br>Currency: %{customdata[0]}<br>Original Value: %{customdata[1]:,.2f}<extra></extra>'
            )
            
            # Apply styling
            fig.update_layout(
                height=450,
                margin=dict(l=20, r=20, t=30, b=20),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key="category_breakdown_sunburst")
        
        # Treemap
        with category_tabs[2]:
            fig = px.treemap(
                category_breakdown,
                path=['Category'],
                values='ValueUSD',
                color='Category',
                color_discrete_map=category_colors,
                hover_data=['Percentage'],
                title='Portfolio Distribution by Category'
            )
            
            fig.update_traces(
                textinfo='label+value+percent root',
                hovertemplate='<b>%{label}</b><br>Value: $%{value:,.2f}<br>Percentage: %{customdata[0]:.1f}%<extra></extra>'
            )
            
            # Apply styling
            fig.update_layout(
                height=350,
                margin=dict(l=20, r=20, t=30, b=20),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key="category_breakdown_treemap")
# CHUNK 12: Enhanced Category Breakdown Function (Third Part - Radar) and Investment Change Table (First Part)
        # Radar Chart (for category distribution)
        with category_tabs[3]:
            # Radar chart needs data in a specific format
            categories = category_breakdown['Category'].tolist()
            values = category_breakdown['Percentage'].tolist()
            
            # Create radar chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name='Portfolio Distribution',
                line_color='#4cc9f0',
                fillcolor='rgba(76, 201, 240, 0.3)'
            ))
            
            # Apply styling
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, max(values) * 1.1]
                    )
                ),
                height=400,
                margin=dict(l=20, r=20, t=30, b=20),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                title='Portfolio Distribution by Category (Radar View)'
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key="category_breakdown_radar")
    else:
        st.info("No data available. Please add investment entries.")

def create_investment_change_table(latest_df, df, latest_date):
    """Create an enhanced investment change table with thematic colors for gains/losses"""
    if not latest_df.empty:
        st.subheader("Investment Value Changes")
        
        try:
            # Get the latest date data
            latest_values = latest_df.copy()
            
            # Create a dictionary to track the most recent actual update for each investment
            last_modified_dates = {}
            
            # Process all entries in reverse chronological order to find when each investment was actually changed
            for date in sorted(df['Date'].unique(), reverse=True):
                date_df = df[df['Date'] == date]
                
                for _, row in date_df.iterrows():
                    inv = row['Investment']
# CHUNK 13: Investment Change Table Function (Second Part)
                    # If we haven't recorded this investment yet, check if there's an earlier entry with a different value
                    if inv not in last_modified_dates:
                        # Find all earlier entries for this investment
                        earlier_entries = df[(df['Date'] < date) & (df['Investment'] == inv)].sort_values('Date', ascending=False)
                        
                        if not earlier_entries.empty:
                            # Get the most recent previous entry
                            prev_entry = earlier_entries.iloc[0]
                            
                            # Compare values to see if it changed
                            if prev_entry['Value'] != row['Value']:
                                # Value changed, so this is the actual last update date
                                last_modified_dates[inv] = date
                            else:
                                # Value didn't change, so use the previous date
                                for prev_date in sorted(df[df['Investment'] == inv]['Date'].unique(), reverse=True):
# CHUNK 14: Investment Change Table Function (Third Part)
                                    if prev_date < date:
                                        # Find entries on or before this date with different values
                                        temp_earlier = df[(df['Date'] <= prev_date) & 
                                                        (df['Investment'] == inv) & 
                                                        (df['Value'] != row['Value'])].sort_values('Date', ascending=False)
                                        
                                        if not temp_earlier.empty:
                                            last_modified_dates[inv] = prev_date
                                            break
                                        else:
                                            last_modified_dates[inv] = prev_date
                        else:
                            # This is the first entry for this investment
                            last_modified_dates[inv] = date
            
            # Get all dates except the latest one
            previous_dates = df[df['Date'] < latest_date]['Date'].unique()
            
            if len(previous_dates) > 0:
                # Find changes for each investment
                changes_data = []
                
                for _, row in latest_values.iterrows():
                    inv = row['Investment']
                    current_value = row['Value']
                    currency = row['Currency']
                    current_value_usd = row['ValueUSD']
                    
                    # Find the most recent previous entry for this investment
                    prev_entries = df[(df['Date'] < latest_date) & (df['Investment'] == inv)].sort_values('Date', ascending=False)
                    
                    if not prev_entries.empty:
                        # Get the most recent previous entry
                        prev_row = prev_entries.iloc[0]
                        prev_date = prev_row['Date']
                        prev_value = prev_row['Value']
                        prev_value_usd = prev_row['ValueUSD']
                        
                        # Calculate changes - with careful handling of edge cases
                        change = current_value - prev_value if prev_value is not None else 0
                        change_pct = ((current_value / prev_value) - 1) * 100 if prev_value and prev_value > 0 else 0

                        change_usd = current_value_usd - prev_value_usd if prev_value_usd is not None else 0
                        change_usd_pct = ((current_value_usd / prev_value_usd) - 1) * 100 if prev_value_usd and prev_value_usd > 0 else 0
# CHUNK 15: Investment Change Table Function (Fourth Part)
                        # Get the actual last modified date for this investment
                        actual_last_update = last_modified_dates.get(inv, prev_date)
                        
                        # Calculate days between actual updates
                        days_between = (latest_date - actual_last_update).days if inv in last_modified_dates else "N/A"
                        
                        # Add to results with formatted strings
                        changes_data.append({
                            "Investment": inv,
                            "Current Value": f"{current_value:,.2f} {currency}",
                            "Current Value (USD)": f"${current_value_usd:,.2f}",
                            "Change": f"{change:+,.2f} {currency} ({change_pct:+.2f}%)",
                            "Change (USD)": f"${change_usd:+,.2f} ({change_usd_pct:+.2f}%)",
                            "Previous Update": f"{days_between} days ago" if isinstance(days_between, int) else days_between,
                            "_sort_value": abs(change_usd),  # For sorting
                            "_change_color": "positive" if change_usd > 0 else ("neutral" if change_usd == 0 else "negative"),
                            "_change_value": change_usd_pct,  # Store raw value for color intensity
                            "_actual_change_usd": change_usd  # Store the actual dollar change (can be negative)
                        })
                    else:
                        # No previous data for this investment
                        changes_data.append({
                            "Investment": inv,
                            "Current Value": f"{current_value:,.2f} {currency}",
                            "Current Value (USD)": f"${current_value_usd:,.2f}",
                            "Change": "N/A",
                            "Change (USD)": "N/A",
                            "Previous Update": "No prior data",
                            "_sort_value": 0,  # For sorting
                            "_change_color": "neutral",
                            "_change_value": 0,
                            "_actual_change_usd": 0  # Add this field with zero value
                        })
# CHUNK 16: Investment Change Table Function (Fifth Part)
                # Create DataFrame and sort by magnitude of change
                if changes_data:
                    try:
                        # Create DataFrame from our collected data
                        changes_df = pd.DataFrame(changes_data)
                        
                        # Create tabs for different sorting options
                        sort_tabs = st.tabs(["By Magnitude", "By Investment", "By Value"])

                        # Helper function to extract numeric values from currency strings
                            def extract_numeric_value(value_str):
                                if isinstance(value_str, str):
                                    # Extract the first numeric part from strings like "$1,234.56 (5.67%)"
                                    # This finds any sequence of digits, possibly with commas and a decimal point
                                    import re
                                    matches = re.findall(r'[-+]?[\d,]+\.?\d*', value_str)
                                    if matches:
                                        # Take the first match and remove commas
                                        return float(matches[0].replace(',', ''))
                                return 0.0  # Default value if extraction fails

                            # Custom function to apply color styling to each tab's dataframe
                            def apply_color_styling(df_to_style):
                                # Create a copy that includes both display columns and style metadata
                                styling_df = changes_df.copy()
                                
                                # Function to generate CSS styles based on change direction
                                def style_row(row):
                                    color = row.get('_change_color', 'neutral')
                                    
                                    # Apply distinct styling based on change direction
                                    if color == 'positive':
                                        # Green background with white text for positive changes
                                        return ['background-color: #22c55e; color: white;'] * len(df_to_style.columns)
                                    elif color == 'negative':
                                        # Red background with white text for negative changes
                                        return ['background-color: #ef4444; color: white;'] * len(df_to_style.columns)
                                    else:
                                        # Neutral styling - keep as is with subtle background
                                        return ['background-color: rgba(156, 163, 175, 0.1); color: #9ca3af;'] * len(df_to_style.columns)
                                
                                # Apply styling to each row
                                styled_df = df_to_style.style.apply(
                                    lambda row: style_row(
                                        styling_df[styling_df['Investment'] == row['Investment']].iloc[0] 
                                        if not styling_df[styling_df['Investment'] == row['Investment']].empty 
                                        else {}
                                    ), 
                                    axis=1
                                )
                                
                                return styled_df

                            with sort_tabs[0]:
                                st.dataframe(
                                    apply_color_styling(sort_by_magnitude(display_df)),
                                    use_container_width=True,
                                    hide_index=True,
                                    column_config={
                                        "Investment": st.column_config.TextColumn("Investment"),
                                        "Current Value": st.column_config.TextColumn("Current Value"),
                                        "Current Value (USD)": st.column_config.TextColumn("Current Value (USD)"),
                                        "Change": st.column_config.TextColumn("Change"),
                                        "Change (USD)": st.column_config.TextColumn("Change (USD)"),
                                        "Previous Update": st.column_config.TextColumn("Previous Update")
                                    }
                                )

                            with sort_tabs[1]:
                                st.dataframe(
                                    apply_color_styling(sort_by_investment(display_df)),
                                    use_container_width=True,
                                    hide_index=True,
                                    column_config={
                                        "Investment": st.column_config.TextColumn("Investment"),
                                        "Current Value": st.column_config.TextColumn("Current Value"),
                                        "Current Value (USD)": st.column_config.TextColumn("Current Value (USD)"),
                                        "Change": st.column_config.TextColumn("Change"),
                                        "Change (USD)": st.column_config.TextColumn("Change (USD)"),
                                        "Previous Update": st.column_config.TextColumn("Previous Update")
                                    }
                                )

                            with sort_tabs[2]:
                                st.dataframe(
                                    apply_color_styling(sort_by_value(display_df)),
                                    use_container_width=True,
                                    hide_index=True,
                                    column_config={
                                        "Investment": st.column_config.TextColumn("Investment"),
                                        "Current Value": st.column_config.TextColumn("Current Value"),
                                        "Current Value (USD)": st.column_config.TextColumn("Current Value (USD)"),
                                        "Change": st.column_config.TextColumn("Change"),
                                        "Change (USD)": st.column_config.TextColumn("Change (USD)"),
                                        "Previous Update": st.column_config.TextColumn("Previous Update")
                                    }
                                )
# END OF REPLACEMENT BLOCK
                    # Add summary statistics
                    summary_col1, summary_col2 = st.columns(2)
                    
                    with summary_col1:
                        # Calculate total changes - use the actual dollar change values directly
                        total_change_usd = sum([row.get("_actual_change_usd", 0) for _, row in changes_df.iterrows() if row.get("_change_color", "") != "neutral"])
                        
                        st.metric(
                            "Total Portfolio Change",
                            f"${total_change_usd:,.2f}",
                            f"{(total_change_usd/latest_df['ValueUSD'].sum() * 100):.2f}%" if latest_df['ValueUSD'].sum() > 0 else None,
                            delta_color="normal" if total_change_usd >= 0 else "inverse"
                        )
# CHUNK 18: Investment Change Table Function (Seventh Part)
                    with summary_col2:
                        # Count investments with positive and negative changes
                        positive_changes = sum([1 for _, row in changes_df.iterrows() if row["_change_color"] == "positive"])
                        negative_changes = sum([1 for _, row in changes_df.iterrows() if row["_change_color"] == "negative"])
                        neutral_changes = sum([1 for _, row in changes_df.iterrows() if row["_change_color"] == "neutral"])
                        
                        st.write("Investment Changes:")
                        st.markdown(f"""
                        <div style="display: flex; justify-content: space-around; text-align: center;">
                            <div>
                                <div style="font-size: 24px; color: #4ade80;">↑ {positive_changes}</div>
                                <div style="font-size: 12px;">Positive</div>
                            </div>
                            <div>
                                <div style="font-size: 24px; color: #f87171;">↓ {negative_changes}</div>
                                <div style="font-size: 12px;">Negative</div>
                            </div>
                            <div>
                                <div style="font-size: 24px; color: #9ca3af;">⟷ {neutral_changes}</div>
                                <div style="font-size: 12px;">Neutral/New</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No investment changes to display.")
            else:
                st.info("No historical data available for comparison.")
        except Exception as e:
            st.error(f"Error calculating investment changes: {str(e)}")
    else:
        st.info("No data available. Please add investment entries.")
# CHUNK 19: Portfolio Performance Chart Function (First Part)
def create_portfolio_performance_chart(df, latest_date):
    """Create enhanced portfolio performance chart with thematic colors and animations"""
    if not df.empty:
        st.subheader("Portfolio Performance Over Time")
        
        # Create tabs for different time periods
        # Create tabs for different time periods including Custom option
        period_tabs = st.tabs(["1 Month", "3 Months", "6 Months", "1 Year", "YTD", "All Time", "Custom"])
        
        # Define time periods
        time_periods = {
            "1 Month": timedelta(days=30),
            "3 Months": timedelta(days=90),
            "6 Months": timedelta(days=180),
            "1 Year": timedelta(days=365),
            "YTD": None,  # Special case, handled separately
            "All Time": None,  # Special case, use all data
            "Custom": "custom"  # Special case, will use date picker
        }
        
        # Function to get data for a specific time period
        # Function to get data for a specific time period
# REPLACE THIS BLOCK IN dashboard_components.py (the custom tab handling)
        # Function to get data for a specific time period
        def get_period_data(period):
            if period == "Custom":
                # For Custom period, show date pickers and let user select range
                
                # Initialize session state for custom date range if not already done
                if 'custom_start_date' not in st.session_state:
                    st.session_state.custom_start_date = df['Date'].min().date()
                if 'custom_end_date' not in st.session_state:
                    st.session_state.custom_end_date = latest_date
                
                # Create columns for date pickers
                custom_cols = st.columns([1, 1, 1])
                with custom_cols[0]:
                    earliest_available = df['Date'].min().date()
                    start_date = st.date_input(
                        "From date",
                        value=st.session_state.custom_start_date,
                        min_value=earliest_available,
                        max_value=latest_date,
                        key="custom_start_date"
                    )
                
                with custom_cols[1]:
                    end_date = st.date_input(
                        "To date",
                        value=st.session_state.custom_end_date,
                        min_value=earliest_available,
                        max_value=latest_date,
                        key="custom_end_date"
                    )
                
                with custom_cols[2]:
                    if st.button("Apply Date Range", key="apply_custom_range"):
                        st.session_state.custom_start_date = start_date
                        st.session_state.custom_end_date = end_date
                
                # Use the selected date range
                custom_start = pd.Timestamp(st.session_state.custom_start_date)
                custom_end = pd.Timestamp(st.session_state.custom_end_date)
                
                # Filter data for the user-selected period
                period_df = df[(df['Date'] >= custom_start) & (df['Date'] <= custom_end)]
                
                if period_df.empty:
                    st.warning("No data available for the selected date range.")
                    return None
                
                # Group by date and sum values
                return period_df.groupby('Date')['ValueUSD'].sum().reset_index()                
            elif period == "All Time":
                start_date = df['Date'].min()
            elif period == "YTD":
                # Convert latest_date to pandas Timestamp if it's a date object
                year = latest_date.year
                month = 1
                day = 1
                start_date = pd.Timestamp(year=year, month=month, day=day)
            else:
                # Convert timedelta subtraction result to pandas Timestamp
                delta = time_periods[period]
                # Convert latest_date to pandas Timestamp if it's not already
                latest_timestamp = pd.Timestamp(latest_date)
                start_date = latest_timestamp - delta
            
            # Filter data for the period - now both sides of the comparison are pandas Timestamps
            period_df = df[df['Date'] >= start_date]
            
            if period_df.empty:
                return None
            
            # Group by date and sum values
            return period_df.groupby('Date')['ValueUSD'].sum().reset_index()
# CHUNK 20: Portfolio Performance Chart Function (Second Part)
        # Create charts for each period
        for i, period in enumerate(time_periods.keys()):
            with period_tabs[i]:
                period_data = get_period_data(period)
                
                if period_data is not None and len(period_data) > 1:
                    # Add smoothing option
                    smoothing = st.slider(
                        "Line Smoothing",
                        min_value=0,
                        max_value=10,
                        value=0,
                        help="Higher values create smoother lines",
                        key=f"smoothing_{period}"
                    )
                    
                    # Add visualization options
                    chart_type = st.radio(
                        "Chart Type",
                        ["Line", "Area", "Bar", "Candlestick-like"],
                        horizontal=True,
                        key=f"chart_type_{period}"
                    )
                    
                    # Determine performance color
                    start_value = period_data.iloc[0]['ValueUSD']
                    end_value = period_data.iloc[-1]['ValueUSD']
                    pct_change = ((end_value / start_value) - 1) * 100 if start_value > 0 else 0
                    
                    if pct_change >= 3:
                        line_color = "#4ade80"  # Strong positive (green)
                    elif pct_change > 0:
                        line_color = "#86efac"  # Slight positive (light green)
                    elif pct_change == 0:
                        line_color = "#9ca3af"  # Neutral (gray)
                    elif pct_change > -3:
                        line_color = "#fca5a5"  # Slight negative (light red)
                    else:
                        line_color = "#f87171"  # Strong negative (red)
# CHUNK 21: Portfolio Performance Chart Function (Third Part)
                    # Create visualization based on type
                    if chart_type == "Line":
                        fig = px.line(
                            period_data,
                            x='Date',
                            y='ValueUSD',
                            labels={'ValueUSD': 'Total Value (USD)', 'Date': 'Date'},
                            title=f'Portfolio Value Over {period}',
                            line_shape='spline' if smoothing > 0 else 'linear'
                        )
                        fig.update_traces(line=dict(width=3, color=line_color))

                    elif chart_type == "Area":
                        fig = px.area(
                            period_data,
                            x='Date',
                            y='ValueUSD',
                            labels={'ValueUSD': 'Total Value (USD)', 'Date': 'Date'},
                            title=f'Portfolio Value Over {period}',
                            line_shape='spline' if smoothing > 0 else 'linear'
                        )
                        fig.update_traces(
                            line=dict(width=2, color=line_color),
                            fillcolor=f"rgba({','.join(str(int(line_color.lstrip('#')[i:i+2], 16)) for i in (0, 2, 4))}, 0.3)"
                        )

                    elif chart_type == "Bar":
                        fig = px.bar(
                            period_data,
                            x='Date',
                            y='ValueUSD',
                            labels={'ValueUSD': 'Total Value (USD)', 'Date': 'Date'},
                            title=f'Portfolio Value Over {period}'
                        )
                        fig.update_traces(marker_color=line_color)
# CHUNK 22: Portfolio Performance Chart Function (Fourth Part - Candlestick)
                    else:  # Candlestick-like
                        # Create a candlestick-like visualization
                        # First, calculate some additional metrics
                        if len(period_data) > 1:
                            # For each date, calculate high/low based on neighboring points
                            candlestick_data = []
                            for i in range(len(period_data)):
                                row = period_data.iloc[i]
                                # Base value
                                base_value = row['ValueUSD']
                                
                                # Add some variation for high/low to simulate candlestick
                                if i > 0:
                                    prev_value = period_data.iloc[i-1]['ValueUSD']
                                    change = base_value - prev_value
                                    high = base_value + abs(change) * 0.1
                                    low = base_value - abs(change) * 0.1
                                else:
                                    # For the first point
                                    high = base_value * 1.02
                                    low = base_value * 0.98
                                
                                candlestick_data.append({
                                    'Date': row['Date'],
                                    'Open': base_value * 0.99 if i > 0 else base_value,
                                    'High': high,
                                    'Low': low,
                                    'Close': base_value,
                                })

                            candlestick_df = pd.DataFrame(candlestick_data)
                            
                            # Create the figure manually
                            fig = go.Figure()
                            
                            # Add candlestick
                            fig.add_trace(go.Candlestick(
                                x=candlestick_df['Date'],
                                open=candlestick_df['Open'],
                                high=candlestick_df['High'],
                                low=candlestick_df['Low'],
                                close=candlestick_df['Close'],
                                name='Portfolio Value',
                                increasing_line_color='#26a69a', 
                                decreasing_line_color='#ef5350'
                            ))

                            # Add a line trace for the closing values
                            fig.add_trace(go.Scatter(
                                x=candlestick_df['Date'],
                                y=candlestick_df['Close'],
                                line=dict(color='rgba(255, 255, 255, 0.5)', width=1),
                                name='Trend Line'
                            ))
# CHUNK 23: Portfolio Performance Chart Function (Fifth Part)
                        else:
                            # Fall back to line chart if not enough data points
                            fig = px.line(
                                period_data,
                                x='Date',
                                y='ValueUSD',
                                labels={'ValueUSD': 'Total Value (USD)', 'Date': 'Date'},
                                title=f'Portfolio Value Over {period}'
                            )
                    
                    # Add performance indicators
                    fig.add_annotation(
                        x=period_data.iloc[-1]['Date'],
                        y=period_data.iloc[-1]['ValueUSD'],
                        text=f"{pct_change:+.2f}% over {period}",
                        showarrow=True,
                        arrowhead=1,
                        ax=0,
                        ay=-40,
                        font=dict(color="white"),
                        bgcolor=line_color,
                        bordercolor=line_color,
                        borderwidth=2,
                        borderpad=4,
                        opacity=0.8
                    )
                    
                    # Apply styling with dark mode and animation effects
                    fig.update_layout(
                        height=400,
                        margin=dict(l=20, r=20, t=30, b=20),
                        xaxis_title="Date",
                        yaxis_title="Value (USD)",
                        hovermode="x unified",
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        xaxis=dict(
                            showgrid=True,
                            gridcolor='rgba(255,255,255,0.1)'
                        ),
                        yaxis=dict(
                            showgrid=True,
                            gridcolor='rgba(255,255,255,0.1)'
                        )
                    )
# CHUNK 24: Portfolio Performance Chart Function (Sixth Part)
                    # Add performance metrics under the chart
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True}, key=f"performance_{period}_{chart_type}")
                    
                    # Display summary metrics
                    metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                    
                    with metrics_col1:
                        start_date = period_data.iloc[0]['Date']
                        end_date = period_data.iloc[-1]['Date']
                        st.metric(
                            "Period",
                            f"{start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}",
                            f"{(end_date - start_date).days} days"
                        )
                    
                    with metrics_col2:
                        st.metric(
                            "Start Value",
                            f"${start_value:,.2f}",
                            None
                        )
                    
                    with metrics_col3:
                        st.metric(
                            "End Value",
                            f"${end_value:,.2f}",
                            f"{pct_change:+.2f}%",
                            delta_color="normal" if pct_change >= 0 else "inverse"
                        )
# CHUNK 25: Portfolio Performance Chart Function (Seventh Part - Volatility Analysis)
                    # Add volatility analysis
                    if (end_date - start_date).days >= 30 and len(period_data) > 5:
                        st.subheader("Volatility Analysis")
                        
                        # Calculate daily returns
                        period_data['Return'] = period_data['ValueUSD'].pct_change() * 100
                        period_data = period_data.dropna()
                        
                        # Calculate volatility metrics
                        volatility = period_data['Return'].std()
                        max_drawdown = 0
                        peak = period_data.iloc[0]['ValueUSD']
                        
                        for _, row in period_data.iterrows():
                            if row['ValueUSD'] > peak:
                                peak = row['ValueUSD']
                            drawdown = (peak - row['ValueUSD']) / peak * 100
                            max_drawdown = max(max_drawdown, drawdown)
                        
                        vol_col1, vol_col2 = st.columns(2)
                        
                        with vol_col1:
                            st.metric(
                                "Daily Volatility",
                                f"{volatility:.2f}%",
                                None
                            )
                        
                        with vol_col2:
                            st.metric(
                                "Maximum Drawdown",
                                f"{max_drawdown:.2f}%",
                                None,
                                delta_color="inverse"
                            )
# CHUNK 26: Portfolio Performance Chart Function (Eighth Part)
                        # Determine range for the histogram based on data
                        min_return = min(period_data['Return'])
                        max_return = max(period_data['Return'])

                        # Ensure range is at least -5% to +5% for readability
                        min_bin = max(min(floor(min_return), -5), -10)
                        max_bin = min(max(ceil(max_return), 5), 10)

                        # Create 1.0% increment bins
                        bin_size = 1.0  # 1.0% increments
                        bins = np.arange(min_bin, max_bin + bin_size, bin_size)

                        # Create custom histogram with 1% increments
                        fig = go.Figure()

                        # Add histogram trace with custom bins
                        fig.add_trace(go.Histogram(
                            x=period_data['Return'],
                            xbins=dict(
                                start=min_bin,
                                end=max_bin,
                                size=bin_size
                            ),
                            name='Daily Returns',
                            marker=dict(
                                color=period_data['Return'],
                                colorscale=[
                                    [0.0, '#ef4444'],     # Deeply negative (red)
                                    [0.2, '#f87171'],     # Negative (lighter red)
                                    [0.4, '#fcd34d'],     # Slightly negative (yellow-orange)
                                    [0.5, '#facc15'],     # Neutral (yellow)
                                    [0.6, '#bef264'],     # Slightly positive (yellow-green)
                                    [0.8, '#86efac'],     # Positive (lighter green)
                                    [1.0, '#22c55e']      # Strongly positive (green)
                                ],
                                # Important: use actual min/max values for proper scaling
                                cmin=min(min_bin, -5),    # Ensure negative range is covered
                                cmax=max(max_bin, 5),     # Ensure positive range is covered
                                cmid=0,                   # Set the midpoint of the color scale to 0
                                colorbar=dict(
                                    title=dict(
                                        text='Return %',
                                        side='right'
                                    )
                                )
                            )
                        ))

                        # Update layout for the histogram
                        fig.update_layout(
                            title='Daily Returns Distribution',
                            height=350,
                            margin=dict(l=20, r=20, t=30, b=20),
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            xaxis=dict(
                                title='Daily Return (%)',
                                tickmode='linear',
                                tick0=min_bin,
                                dtick=bin_size,  # 1% increments
                                showgrid=True,
                                gridcolor='rgba(255,255,255,0.1)',
                                zeroline=True,
                                zerolinecolor='rgba(255,255,255,0.5)',
                                zerolinewidth=2
                            ),
                            yaxis=dict(
                                title='Frequency (Days)',
                                showgrid=True,
                                gridcolor='rgba(255,255,255,0.1)'
                            ),
                            bargap=0.1
                        )

                        # Add a vertical line at 0% for reference
                        fig.add_shape(
                            type='line',
                            x0=0, y0=0,
                            x1=0, y1=1,
                            yref='paper',
                            line=dict(
                                color='rgba(255,255,255,0.5)',
                                width=2,
                                dash='dash'
                            )
                        )
                        
                        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key=f"returns_dist_{period}")
                else:
                    st.info(f"Not enough data available for {period} visualization.")
    else:
        st.info("No data available. Please add investment entries.")
# CHUNK 27: Enhanced CSS Function
def create_enhanced_css():
    """Create enhanced CSS for dashboard theming"""
    return """
    <style>
        /* General page styling */
        .main .block-container {
            padding-top: 2rem;
            max-width: 1200px;
        }
        
        /* Dark mode theme */
        :root {
            --background-color: #1e1e2e;
            --text-color: #ffffff;
            --card-bg: #2c2c40;
            --card-border: #3d3d54;
            --positive-color: #4ade80;
            --negative-color: #f87171;
            --neutral-color: #9ca3af;
            --primary-color: #4cc9f0;
            --secondary-color: #7209b7;
            --accent-color: #f72585;
        }
        
        /* Improved tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0;
            background-color: var(--background-color);
            padding: 0;
            border-radius: 8px;
            display: flex;
            overflow: hidden;
            border: 1px solid var(--card-border);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 70px;
            white-space: pre-wrap;
            background-color: var(--card-bg);
            border-radius: 0;
            padding: 10px 20px;
            font-weight: 600;
            color: white;
            min-width: 150px;
            text-align: center;
            border-right: 1px solid var(--card-border);
            transition: all 0.3s ease;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
# CHUNK 28: Enhanced CSS Function (Continued)
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #3d3d54;
            transform: translateY(-2px);
        }
        
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background-color: #4361ee;
            box-shadow: 0 0 10px rgba(67, 97, 238, 0.5);
        }
        
        /* Dashboard header styling */
        .dashboard-header {
            text-align: center;
            margin-bottom: 2rem;
            padding: 1rem;
            background: linear-gradient(90deg, #4cc9f0, #4361ee, #7209b7);
            border-radius: 8px;
            color: white;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }
        
        .dashboard-header h1 {
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
        }
        
        .dashboard-header .subtitle {
            font-size: 1.1rem;
            opacity: 0.9;
            margin-top: 0.5rem;
        }
        
        /* Metric card styling */
        .metric-card {
            display: flex;
            align-items: center;
            padding: 1rem;
            background-color: var(--card-bg);
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease;
            height: 100%;
            overflow: hidden;
            position: relative;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.3);
        }
# CHUNK 29: Enhanced CSS Function (More Continued)
        .metric-card::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 5px;
            background: linear-gradient(90deg, #4cc9f0, #4361ee);
        }
        
        .metric-card.positive-change::after {
            background: linear-gradient(90deg, #4ade80, #22c55e);
        }
        
        .metric-card.negative-change::after {
            background: linear-gradient(90deg, #f87171, #dc2626);
        }
        
        .metric-card.total-value::after {
            background: linear-gradient(90deg, #4cc9f0, #3b82f6);
        }
        
        .metric-card .metric-icon {
            font-size: 2rem;
            margin-right: 1rem;
            display: flex;
            align-items: center;
            justify-content: center;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background-color: rgba(255, 255, 255, 0.1);
        }
        
        .metric-card .metric-content {
            flex: 1;
        }
        
        .metric-card h3 {
            margin: 0;
            font-size: 0.9rem;
            font-weight: 600;
            opacity: 0.8;
        }
        
        .metric-card .metric-value {
            margin: 0.5rem 0 0 0;
            font-size: 1.5rem;
            font-weight: 700;
        }
        
        .positive-change .metric-value {
            color: var(--positive-color);
        }
        
        .negative-change .metric-value {
            color: var(--negative-color);
        }
# CHUNK 30: Enhanced CSS Function (Final Part) and Theme Toggle Function
        /* Improved dataframe styling */
        [data-testid="stDataFrame"] {
            background-color: var(--card-bg);
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid var(--card-border);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        }
        
        [data-testid="stDataFrame"] th {
            background-color: rgba(0, 0, 0, 0.2);
            font-weight: 600;
        }
        
        /*
# CHUNK 31: Final CSS Elements and Theme Toggle Function
        /* Additional styling for better readability */
        .block-container {
            padding-bottom: 3rem;
        }
        
        /* Add animation effects */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .animate-in {
            animation: fadeIn 0.5s ease-out forwards;
        }
        
        /* Add styling for icons */
        .tab-icon {
            font-size: 32px;
            display: inline-block;
            width: 32px;
            text-align: center;
            line-height: 32px;
            margin-right: 8px;
        }

        .action-icon {
            font-size: 28px;
            display: inline-block;
            width: 28px;
            text-align: center;
            line-height: 28px;
            margin-right: 8px;
        }

        .small-icon {
            font-size: 24px;
            display: inline-block;
            width: 24px;
            text-align: center;
            line-height: 24px;
            margin-right: 8px;
        }
        
        /* Visual improvements for charts */
        [data-testid="stPlotlyChart"] {
            background-color: var(--card-bg);
            border-radius: 8px;
            padding: 1rem;
            border: 1px solid var(--card-border);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease;
        }
        
        [data-testid="stPlotlyChart"]:hover {
            box-shadow: 0 6px 10px rgba(0, 0, 0, 0.3);
        }
    </style>
    """

def apply_theme_mode_toggle():
    """Add a theme mode toggle (light/dark) with improved UI"""
    theme_col1, theme_col2 = st.sidebar.columns([4, 1])
    
    with theme_col1:
        st.markdown("### Theme Settings")
    
    with theme_col2:
        # This is just a placeholder since Streamlit doesn't allow true dynamic theming
        # In a real application, you would implement JavaScript for theme switching
        if st.button("🌙", help="Toggle theme"):
            pass
    
    # Add color scheme selector
    color_scheme = st.sidebar.selectbox(
        "Color Scheme",
        ["Blue Ocean", "Forest Green", "Sunset Orange", "Royal Purple", "Midnight"],
        index=0
    )
    
    st.sidebar.markdown("*Theme settings are visual only in this demo*")
    
    return color_scheme
# CHUNK 32: Enhanced Dashboard Function
def create_enhanced_dashboard(df, latest_df, latest_date, INVESTMENT_CATEGORIES, INVESTMENT_ACCOUNTS):
    """Create the complete enhanced dashboard with all components"""
    # Apply enhanced CSS
    st.markdown(create_enhanced_css(), unsafe_allow_html=True)
    
    # Create dashboard header
    create_dashboard_header()
    
    # Create themed metrics with enhanced styling
    create_themed_metrics(latest_df, df, latest_date)
    
    # Add separator
    st.markdown("<hr style='margin: 2rem 0; opacity: 0.3;'>", unsafe_allow_html=True)
    
    # Create investment value changes table
    create_investment_change_table(latest_df, df, latest_date)
    
    # Add separator
    st.markdown("<hr style='margin: 2rem 0; opacity: 0.3;'>", unsafe_allow_html=True)
    
    # Create portfolio performance chart
    create_portfolio_performance_chart(df, latest_date)
    
    # Add separator
    st.markdown("<hr style='margin: 2rem 0; opacity: 0.3;'>", unsafe_allow_html=True)
    
    # Add charts in a 2-column layout
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # Create enhanced asset allocation charts
        create_enhanced_asset_allocation(latest_df, INVESTMENT_CATEGORIES)
    
    with chart_col2:
        # Create enhanced currency breakdown charts
        create_enhanced_currency_breakdown(latest_df)
    
    # Add separator
    st.markdown("<hr style='margin: 2rem 0; opacity: 0.3;'>", unsafe_allow_html=True)
    
    # Create category breakdown charts (full width)
    create_enhanced_category_breakdown(latest_df, INVESTMENT_CATEGORIES)
# CHUNK 33: Create Dashboard Components Module Function
# Function to create the dashboard_components.py file
def create_dashboard_components_module(file_path="dashboard_components.py"):
    """
    Create a dashboard_components.py file with all the enhanced dashboard components
    
    Args:
        file_path (str): The path to save the dashboard_components.py file
    """
    # Get all the function definitions from this module
    import inspect
    import sys
    
    # Get all functions defined in this module
    current_module = sys.modules[__name__]
    function_names = [
        'create_dashboard_header',
        'create_themed_metrics',
        'create_enhanced_asset_allocation',
        'create_enhanced_currency_breakdown',
        'create_enhanced_category_breakdown',
        'create_investment_change_table',
        'create_portfolio_performance_chart',
        'create_enhanced_css',
        'apply_theme_mode_toggle',
        'create_enhanced_dashboard'
    ]
    
    # Create the file content
    file_content = """# dashboard_components.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

"""
    
    # Add each function definition
    for func_name in function_names:
        if hasattr(current_module, func_name):
            func = getattr(current_module, func_name)
            func_source = inspect.getsource(func)
            file_content += func_source + "\n\n"
    
    # Write the file
    with open(file_path, 'w') as f:
        f.write(file_content)
    
    return file_path
