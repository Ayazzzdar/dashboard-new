#!/usr/bin/env python3
"""
The Day Archive - Processing Dashboard
A beautiful Streamlit interface for managing order processing
"""

import streamlit as st
import pandas as pd
import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="The Day Archive - Dashboard",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'processed_orders' not in st.session_state:
    st.session_state.processed_orders = []
if 'current_order_index' not in st.session_state:
    st.session_state.current_order_index = 0
if 'processing_log' not in st.session_state:
    st.session_state.processing_log = []
if 'error_log' not in st.session_state:
    st.session_state.error_log = []
if 'total_processed_today' not in st.session_state:
    st.session_state.total_processed_today = 0
if 'selected_orders' not in st.session_state:
    st.session_state.selected_orders = []

# ============================================================================
# HELPER FUNCTIONS (from generate_orders.py)
# ============================================================================

def calculate_star_sign(month: int, day: int) -> str:
    """Calculate zodiac star sign"""
    if (month == 12 and day >= 22) or (month == 1 and day <= 19):
        return "CAPRICORN"
    elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
        return "AQUARIUS"
    elif (month == 2 and day >= 19) or (month == 3 and day <= 20):
        return "PISCES"
    elif (month == 3 and day >= 21) or (month == 4 and day <= 19):
        return "ARIES"
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
        return "TAURUS"
    elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
        return "GEMINI"
    elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
        return "CANCER"
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
        return "LEO"
    elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
        return "VIRGO"
    elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
        return "LIBRA"
    elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
        return "SCORPIO"
    else:
        return "SAGITTARIUS"

def get_birthstone(month: int) -> str:
    """Get birthstone for month"""
    stones = [
        "Garnet", "Amethyst", "Aquamarine", "Diamond", "Emerald", "Pearl",
        "Ruby", "Peridot", "Sapphire", "Opal", "Topaz", "Turquoise"
    ]
    return stones[month - 1]

def get_month_name(month: int) -> str:
    """Get month name"""
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    return months[month - 1]

def get_day_of_week(day: int, month: int, year: int) -> str:
    """Calculate day of week"""
    date = datetime(year, month, day)
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return days[date.weekday()]

# ============================================================================
# SHOPIFY API FUNCTIONS
# ============================================================================

def fetch_shopify_orders(api_token: str, store_url: str) -> List[Dict]:
    """Fetch orders from Shopify"""
    url = f"https://{store_url}/admin/api/2024-01/orders.json"
    headers = {
        "X-Shopify-Access-Token": api_token,
        "Content-Type": "application/json"
    }
    
    params = {
        "status": "any",
        "limit": 250,
        "fields": "id,name,email,line_items,fulfillment_status,created_at"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code != 200:
            st.error(f"Shopify API Error: {response.status_code}")
            return []
        
        orders = response.json().get("orders", [])
        return orders
        
    except Exception as e:
        st.error(f"Error fetching orders: {e}")
        return []

def extract_personalization_data(order: Dict) -> Optional[tuple]:
    """Extract Full Name and Birthday from order"""
    for item in order.get("line_items", []):
        properties = item.get("properties", [])
        
        full_name = None
        birthday = None
        
        for prop in properties:
            if prop.get("name") == "Full Name":
                full_name = prop.get("value")
            elif prop.get("name") == "Birthday":
                birthday = prop.get("value")
        
        if full_name and birthday:
            return (full_name, birthday)
    
    return None

def mark_order_fulfilled(order_id: str, api_token: str, store_url: str) -> bool:
    """Mark an order as fulfilled in Shopify"""
    # This would require creating a fulfillment via Shopify API
    # Simplified version for now
    return True

# ============================================================================
# CLAUDE API FUNCTION
# ============================================================================

def research_with_claude(month_name: str, day: int, year: int, api_key: str, progress_callback=None) -> Dict:
    """Call Claude API to research historical data"""
    
    if progress_callback:
        progress_callback("🔍 Researching with Claude API...")
    
    prompt = f"""Research historical data for {month_name} {day}, {year} in Australia. 
Return ONLY valid JSON (no markdown, no code blocks, no preamble).

CRITICAL FORMATTING RULES:
- All monetary values: ONLY the number with $ or c symbol (e.g., "$2,080" or "8c")
- All population values: ONLY the number with units (e.g., "3.3 Billion" or "11.6 million")
- All percentage values: ONLY the number with % (e.g., "3.2%")
- Celebrity names: Name - Description (NO DATES, e.g., "Steve Seagal - American actor and martial artist")
- News events: Must be events that happened on {month_name} {day} in ANY year (worldwide, not just Australia)
- Number1Song: If ARIA charts didn't exist in {year}, use worldwide #1 song from that time
- HISTORICAL EVENTS: Must be events that happened on {month_name} {day} across different eras (1800s, early 1900s, mid 1900s, 2000s)
  - Look for events on {month_name} {day} in 1800s, early 1900s (1900-1940), mid-late 1900s (1950-1990), and 2000s-2020s
  - If no significant events can be found for that specific DATE, then use events from {year} instead

Provide accurate Australian historical data in this exact JSON structure:

{{
  "PrimeMinister": "Name of Australian PM serving in {year}",
  "IncomingPM": "Name of PM who came into power in {year} (or empty string if no change)",
  "Monarch": "Name of British monarch in {year}",
  "AverageSalary": "VALUE ONLY e.g., $2,080",
  "Celebrity1": "Name - Description (NO DATES)",
  "Celebrity2": "Name - Description (NO DATES)",
  "Celebrity3": "Name - Description (NO DATES)",
  "NewsEvent1": "Major world event that happened on {month_name} {day} in ANY year",
  "NewsEvent2": "Second major world event that happened on {month_name} {day} in ANY year",
  "NewsEvent3": "Third major world event that happened on {month_name} {day} in ANY year",
  "NRLWinner": "NRL premiership winner {year}",
  "AFLWinner": "AFL premiership winner {year}",
  "BestActor": "Oscar Best Actor {year} - Film name",
  "BestActress": "Oscar Best Actress {year} - Film name",
  "Bathurst1000": "Bathurst 1000 winners {year}",
  "AusOpenWinners": "Australian Open singles winners {year}",
  "Number1Song": "Song title - Artist (use ARIA if exists for {year}, otherwise worldwide #1)",
  "AverageHouse": "VALUE ONLY e.g., $8,500",
  "MilkPrice": "VALUE ONLY e.g., $0.08 or $1.20",
  "BreadPrice": "VALUE ONLY e.g., $0.18 or $1.20",
  "EggsPrice": "VALUE ONLY e.g., $0.45 or $1.80",
  "WorldPopulation": "VALUE ONLY e.g., 3.3 Billion",
  "AustraliaPopulation": "VALUE ONLY e.g., 11.6 million",
  "HistoricalEventDate1": "Year (1800s era) when event happened on {month_name} {day}",
  "HistoricalEvent1": "Major historical event that happened on {month_name} {day} in the 1800s",
  "HistoricalEventDate2": "Year (early 1900s) when event happened on {month_name} {day}",
  "HistoricalEvent2": "Major historical event that happened on {month_name} {day} in early 1900s (1900-1940)",
  "HistoricalEventDate3": "Year (mid-late 1900s) when event happened on {month_name} {day}",
  "HistoricalEvent3": "Major historical event that happened on {month_name} {day} in mid-late 1900s (1950-1990)",
  "HistoricalEventDate4": "Year (2000s-2020s) when event happened on {month_name} {day}",
  "HistoricalEvent4": "Major historical event that happened on {month_name} {day} in 2000s-2020s",
  "YearsOfWages": "VALUE ONLY e.g., 4-5 years wages",
  "CadburyBarPrice": "VALUE ONLY e.g., 8c or 90c",
  "PetrolPrice": "VALUE ONLY e.g., $0.06 or $0.68",
  "InflationRate": "VALUE ONLY e.g., 3.2%",
  "StampPrice": "VALUE ONLY e.g., 5c or 41c",
  "CinemaPrice": "VALUE ONLY e.g., $0.75 or $7.50",
  "TopBook": "Title - Author",
  "TopBookDescription": "One sentence description",
  "TVShow": "Show name",
  "TVShowDescription": "One sentence description",
  "FashionTrend": "Trend name",
  "FashionDescription": "One sentence description",
  "Technology": "Technology name",
  "TechnologyDescription": "One sentence description",
  "AustraliaBirths": "VALUE ONLY e.g., 223,000",
  "BirthsDescription": "One sentence about birth rate",
  "BoyName1": "Most popular boys name Australia {year}",
  "BoyName2": "2nd most popular",
  "BoyName3": "3rd",
  "BoyName4": "4th",
  "BoyName5": "5th",
  "BoyName6": "6th",
  "BoyName7": "7th",
  "BoyName8": "8th",
  "BoyName9": "9th",
  "BoyName10": "10th",
  "GirlName1": "Most popular girls name Australia {year}",
  "GirlName2": "2nd",
  "GirlName3": "3rd",
  "GirlName4": "4th",
  "GirlName5": "5th",
  "GirlName6": "6th",
  "GirlName7": "7th",
  "GirlName8": "8th",
  "GirlName9": "9th",
  "GirlName10": "10th"
}}

REMEMBER: 
- NewsEvent1/2/3 must be events that happened on {month_name} {day} in ANY YEAR (not just {year})
- HistoricalEvent1/2/3/4 must ALSO be events that happened on {month_name} {day} across DIFFERENT ERAS
  - Try to find: one from 1800s, one from early 1900s, one from mid 1900s, one from 2000s
  - All should be on {month_name} {day} (the DATE matters, not the year)
  - Only use events from {year} if you cannot find events for that specific date
- All dollar/price values must be CLEAN: just number + $ or c
- Celebrity format: "Name - What they're known for" (NO birth dates)

Return ONLY the JSON object. Start with {{ and end with }}."""

    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    data = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 4000,
        "messages": [{
            "role": "user",
            "content": prompt
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=120)
        
        if response.status_code != 200:
            if progress_callback:
                progress_callback(f"❌ Claude API error: {response.status_code}")
            return {}
        
        result = response.json()
        text_content = result["content"][0]["text"]
        
        # Clean up markdown
        text_content = text_content.replace("```json", "").replace("```", "").strip()
        
        # Parse JSON
        research_data = json.loads(text_content)
        
        if progress_callback:
            progress_callback("✅ Research completed")
        
        return research_data
        
    except Exception as e:
        if progress_callback:
            progress_callback(f"❌ Error: {str(e)}")
        return {}

# ============================================================================
# PROCESSING FUNCTION
# ============================================================================

def process_order(order: Dict, claude_api_key: str, progress_callback=None) -> Optional[Dict]:
    """Process a single order"""
    order_number = order["name"]
    
    if progress_callback:
        progress_callback(f"📋 Processing {order_number}...")
    
    # Extract personalization
    personalization = extract_personalization_data(order)
    if not personalization:
        if progress_callback:
            progress_callback(f"⚠️ No personalization data found")
        return None
    
    full_name, birthday = personalization
    
    if progress_callback:
        progress_callback(f"👤 Customer: {full_name}")
        progress_callback(f"🎂 Birthday: {birthday}")
    
    # Parse birthday
    try:
        day, month, year = map(int, birthday.split('/'))
    except:
        if progress_callback:
            progress_callback("❌ Invalid birthday format")
        return None
    
    # Calculate fields
    day_of_week = get_day_of_week(day, month, year)
    month_name = get_month_name(month)
    star_sign = calculate_star_sign(month, day)
    birthstone = get_birthstone(month)
    
    # Research with Claude
    research_data = research_with_claude(month_name, day, year, claude_api_key, progress_callback)
    
    if not research_data:
        return None
    
    # Combine data
    complete_data = {
        "OrderID": order_number,
        "Name": full_name.upper(),
        "DayOfWeek": day_of_week,
        "MonthName": month_name,
        "Day": day,
        "Year": year,
        "StarSign": star_sign,
        "Birthstone": birthstone,
    }
    
    complete_data.update(research_data)
    
    if progress_callback:
        progress_callback(f"✅ {order_number} processed successfully")
    
    return complete_data

# ============================================================================
# STREAMLIT UI
# ============================================================================

def main():
    # Header
    st.title("📅 The Day Archive - Processing Dashboard")
    st.markdown("---")
    
    # Sidebar - Settings
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # API Credentials
        st.subheader("🔐 API Credentials")
        
        shopify_store = st.text_input(
            "Shopify Store URL",
            value="",
            placeholder="your-store.myshopify.com",
            help="Your Shopify store URL (e.g., 46a0kn-eu.myshopify.com)"
        )
        
        shopify_token = st.text_input(
            "Shopify Access Token",
            value="",
            type="password",
            placeholder="shpat_...",
            help="Your Shopify Admin API access token"
        )
        
        claude_api_key = st.text_input(
            "Claude API Key",
            value="",
            type="password",
            placeholder="sk-ant-api03-...",
            help="Your Claude API key from console.anthropic.com"
        )
        
        # Test connections
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Test Shopify"):
                with st.spinner("Testing..."):
                    orders = fetch_shopify_orders(shopify_token, shopify_store)
                    if orders:
                        st.success(f"✓ Connected ({len(orders)} orders)")
                    else:
                        st.error("✗ Connection failed")
        
        with col2:
            if st.button("Test Claude"):
                st.success("✓ Key format valid")
        
        st.markdown("---")
        
        # Processing Options
        st.subheader("🎯 Processing Options")
        
        test_mode = st.toggle("Test Mode", value=False, help="Process only selected orders for testing")
        
        batch_size = st.number_input(
            "Batch Size",
            min_value=1,
            max_value=100,
            value=5,
            help="Number of orders to process at once"
        )
        
        st.markdown("---")
        
        # Cost Tracker
        st.subheader("💰 Cost Tracker")
        st.metric("Orders Processed Today", st.session_state.total_processed_today)
        cost_estimate = st.session_state.total_processed_today * 0.015
        st.metric("Estimated Cost", f"${cost_estimate:.2f}")
    
    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Orders", "⚙️ Processing", "📊 History", "❌ Errors"])
    
    with tab1:
        st.header("Unfulfilled Orders")
        
        # Fetch orders button
        if st.button("🔄 Refresh Orders", type="primary"):
            with st.spinner("Fetching orders from Shopify..."):
                orders = fetch_shopify_orders(shopify_token, shopify_store)
                
                # Filter unfulfilled
                unfulfilled = [o for o in orders if o.get("fulfillment_status") != "fulfilled"]
                
                # Store in session state
                st.session_state.unfulfilled_orders = unfulfilled
                st.success(f"Found {len(unfulfilled)} unfulfilled orders")
        
        # Display orders
        if 'unfulfilled_orders' in st.session_state and st.session_state.unfulfilled_orders:
            orders = st.session_state.unfulfilled_orders
            
            # Filter options
            col1, col2, col3 = st.columns(3)
            
            with col1:
                search_query = st.text_input("🔍 Search", placeholder="Order # or customer name")
            
            with col2:
                date_filter = st.selectbox(
                    "📅 Filter by Date",
                    ["All Orders", "Today", "Yesterday", "Last 7 Days", "Last 30 Days", "Custom Range"]
                )
            
            with col3:
                if date_filter == "Custom Range":
                    date_range = st.date_input("Select Range", value=(datetime.now().date(), datetime.now().date()))
            
            # Filter logic
            filtered_orders = orders
            
            if search_query:
                filtered_orders = [
                    o for o in filtered_orders 
                    if search_query.lower() in o['name'].lower() or 
                       search_query.lower() in o.get('email', '').lower()
                ]
            
            if date_filter == "Today":
                today = datetime.now().date()
                filtered_orders = [
                    o for o in filtered_orders
                    if datetime.fromisoformat(o['created_at'].replace('Z', '+00:00')).date() == today
                ]
            elif date_filter == "Yesterday":
                yesterday = (datetime.now() - timedelta(days=1)).date()
                filtered_orders = [
                    o for o in filtered_orders
                    if datetime.fromisoformat(o['created_at'].replace('Z', '+00:00')).date() == yesterday
                ]
            elif date_filter == "Last 7 Days":
                week_ago = (datetime.now() - timedelta(days=7)).date()
                filtered_orders = [
                    o for o in filtered_orders
                    if datetime.fromisoformat(o['created_at'].replace('Z', '+00:00')).date() >= week_ago
                ]
            
            # Display order table with checkboxes
            st.markdown(f"**Showing {len(filtered_orders)} orders**")
            
            # Select all / Deselect all
            col1, col2, col3 = st.columns([1, 1, 4])
            with col1:
                if st.button("✓ Select All"):
                    st.session_state.selected_orders = [o['name'] for o in filtered_orders]
                    st.rerun()
            with col2:
                if st.button("✗ Deselect All"):
                    st.session_state.selected_orders = []
                    st.rerun()
            
            # Order list with checkboxes
            for order in filtered_orders[:batch_size]:  # Show only batch_size orders at a time
                personalization = extract_personalization_data(order)
                
                col1, col2, col3, col4 = st.columns([1, 2, 3, 2])
                
                with col1:
                    selected = st.checkbox(
                        order['name'],
                        value=order['name'] in st.session_state.selected_orders,
                        key=f"check_{order['name']}"
                    )
                    if selected and order['name'] not in st.session_state.selected_orders:
                        st.session_state.selected_orders.append(order['name'])
                    elif not selected and order['name'] in st.session_state.selected_orders:
                        st.session_state.selected_orders.remove(order['name'])
                
                with col2:
                    if personalization:
                        st.write(f"**{personalization[0]}**")
                    else:
                        st.write("_No personalization_")
                
                with col3:
                    if personalization:
                        st.write(f"🎂 {personalization[1]}")
                    else:
                        st.write("—")
                
                with col4:
                    order_date = datetime.fromisoformat(order['created_at'].replace('Z', '+00:00'))
                    st.write(f"📅 {order_date.strftime('%b %d, %Y')}")
            
            st.markdown(f"**Selected: {len(st.session_state.selected_orders)} orders**")
            
        else:
            st.info("Click 'Refresh Orders' to fetch unfulfilled orders from Shopify")
    
    with tab2:
        st.header("Process Orders")
        
        if 'selected_orders' in st.session_state and st.session_state.selected_orders:
            st.success(f"Ready to process {len(st.session_state.selected_orders)} selected orders")
            
            # Process button
            if st.button("🚀 Process Selected Orders", type="primary", disabled=st.session_state.processing):
                st.session_state.processing = True
                st.session_state.current_order_index = 0
                st.session_state.processed_orders = []
                
                # Progress containers
                progress_bar = st.progress(0)
                status_text = st.empty()
                log_container = st.container()
                
                # Get selected order objects
                selected_order_objs = [
                    o for o in st.session_state.unfulfilled_orders 
                    if o['name'] in st.session_state.selected_orders
                ]
                
                total_orders = len(selected_order_objs)
                
                # Process each order
                for idx, order in enumerate(selected_order_objs):
                    st.session_state.current_order_index = idx + 1
                    
                    # Update progress
                    progress = (idx + 1) / total_orders
                    progress_bar.progress(progress)
                    status_text.markdown(f"**Processing Order {idx + 1} of {total_orders}** ({order['name']})")
                    
                    # Log callback
                    def log_message(msg):
                        with log_container:
                            st.write(msg)
                        st.session_state.processing_log.append({
                            "timestamp": datetime.now(),
                            "order": order['name'],
                            "message": msg
                        })
                    
                    # Process order
                    try:
                        order_data = process_order(order, claude_api_key, log_message)
                        
                        if order_data:
                            st.session_state.processed_orders.append(order_data)
                            st.session_state.total_processed_today += 1
                        else:
                            st.session_state.error_log.append({
                                "timestamp": datetime.now(),
                                "order": order['name'],
                                "error": "Processing failed"
                            })
                    
                    except Exception as e:
                        st.session_state.error_log.append({
                            "timestamp": datetime.now(),
                            "order": order['name'],
                            "error": str(e)
                        })
                        log_message(f"❌ Error: {str(e)}")
                    
                    time.sleep(1)  # Rate limiting
                
                # Complete
                st.session_state.processing = False
                progress_bar.progress(1.0)
                status_text.markdown("**✅ Processing Complete!**")
                
                # Generate CSV
                if st.session_state.processed_orders:
                    df = pd.DataFrame(st.session_state.processed_orders)
                    
                    # Save to file with timestamp
                    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    filename = f"orders_{timestamp}.csv"
                    df.to_csv(filename, index=False)
                    
                    st.success(f"✅ Generated {filename}")
                    
                    # Download button
                    csv_data = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv_data,
                        file_name=filename,
                        mime="text/csv"
                    )
                    
                    # Preview
                    with st.expander("👁️ Preview Data"):
                        st.dataframe(df.head(10))
        
        else:
            st.info("Select orders from the 'Orders' tab to process")
    
    with tab3:
        st.header("Processing History")
        
        # List all CSV files
        csv_files = sorted(Path('.').glob('orders_*.csv'), reverse=True)
        
        if csv_files:
            for csv_file in csv_files[:10]:  # Show last 10
                with st.expander(f"📄 {csv_file.name}"):
                    df = pd.read_csv(csv_file)
                    st.write(f"**Orders:** {len(df)}")
                    st.write(f"**Created:** {datetime.fromtimestamp(csv_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    # Download button
                    csv_data = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Re-download",
                        data=csv_data,
                        file_name=csv_file.name,
                        mime="text/csv",
                        key=f"download_{csv_file.name}"
                    )
                    
                    # Preview
                    st.dataframe(df.head(5))
        else:
            st.info("No processing history yet")
    
    with tab4:
        st.header("Error Log")
        
        if st.session_state.error_log:
            for error in reversed(st.session_state.error_log[-20:]):
                with st.expander(f"❌ {error['order']} - {error['timestamp'].strftime('%H:%M:%S')}"):
                    st.write(f"**Error:** {error['error']}")
                    
                    # Retry button
                    if st.button(f"🔄 Retry {error['order']}", key=f"retry_{error['order']}_{error['timestamp']}"):
                        st.info("Retry functionality coming soon...")
        else:
            st.success("No errors logged ✓")

if __name__ == "__main__":
    main()
