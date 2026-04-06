# The Day Archive - Processing Dashboard

Beautiful web interface for managing order processing with real-time progress tracking, batch processing, and full order management.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_dashboard.txt
```

### 2. Run the Dashboard

```bash
streamlit run dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

---

## 📋 Features

### ✅ Order Management
- **Visual order list** with checkboxes
- **Search & filter** by order number, customer name, or date
- **Date filters:** Today, Yesterday, Last 7 Days, Custom Range
- **Select All / Deselect All** for quick selection
- **Custom batch sizes** for processing odd numbers of orders

### ⚡ Real-Time Processing
- **Live progress bar** showing current order being processed
- **Step-by-step logs** for each order:
  - ✓ Extracted personalization data
  - 🔍 Researching with Claude...
  - ✓ Research complete
  - ✓ Order processed successfully
- **Estimated time remaining**
- **Pause/Resume** capabilities

### 📊 Data Management
- **Automatic CSV generation** with timestamps (no overwriting!)
- **Preview data** before downloading
- **Download any CSV** from history
- **Processing history** showing last 10 generated files

### 💰 Cost Tracking
- **Orders processed today**
- **Estimated Claude API cost** (~$0.015 per order)
- **Real-time cost updates**

### 🔐 Settings
- **Secure API credential storage**
- **Test Shopify connection** button
- **Test Claude API** button
- **Test mode toggle** for safe testing
- **Custom batch size** input

### 📝 Error Handling
- **Error log** showing all failed orders
- **Retry button** for failed orders
- **Detailed error messages**

---

## 🎯 How to Use

### Step 1: Configure Settings

1. Open the **sidebar** (⚙️ Settings)
2. Enter your Shopify and Claude API credentials
3. Click **Test Shopify** and **Test Claude** to verify connections
4. Set your **batch size** (default: 5)
5. Toggle **Test Mode** if you want to test with limited orders

### Step 2: Select Orders

1. Go to **Orders tab**
2. Click **🔄 Refresh Orders** to fetch from Shopify
3. Use **filters** to narrow down orders:
   - Search by order # or customer name
   - Filter by date (Today, Yesterday, etc.)
4. **Check the boxes** for orders you want to process
5. Or use **✓ Select All** to select all visible orders

### Step 3: Process Orders

1. Go to **Processing tab**
2. Review selected orders count
3. Click **🚀 Process Selected Orders**
4. Watch the **real-time progress**:
   - Progress bar updates
   - Live logs for each order
   - Status messages
5. Wait for completion

### Step 4: Download CSV

1. After processing completes, click **📥 Download CSV**
2. CSV filename includes timestamp: `orders_2026-04-06_14-30-45.csv`
3. Upload to Canva Bulk Create
4. Generate your PDFs!

---

## 📂 File Structure

```
.
├── dashboard.py              # Main Streamlit dashboard
├── requirements_dashboard.txt # Python dependencies
├── orders_*.csv              # Generated CSV files (timestamped)
└── README_DASHBOARD.md       # This file
```

---

## 🔧 Advanced Features

### Date Filtering

**Filter by Date Ordered:**
- **Today:** Orders placed today
- **Yesterday:** Orders from yesterday
- **Last 7 Days:** Orders from the past week
- **Last 30 Days:** Orders from the past month
- **Custom Range:** Pick any date range

### Custom Batch Sizes

Instead of fixed batch sizes, you can enter **any number**:
- Process 1 order for quick testing
- Process 7 orders to handle odd batches
- Process 50 orders for large batches

### CSV Naming

All CSVs are saved with timestamps to prevent overwriting:
```
orders_2026-04-06_09-30-15.csv
orders_2026-04-06_14-22-48.csv
orders_2026-04-07_10-15-33.csv
```

### Processing History

View all previously generated CSVs:
- See order count for each file
- See creation timestamp
- Re-download any CSV
- Preview first 5 rows

---

## 💡 Tips & Tricks

### Process Yesterday's Orders Only

1. Go to Orders tab
2. Select date filter: **"Yesterday"**
3. Click **"✓ Select All"**
4. Process!

### Handle Odd Number of Orders

If you have 7 orders but batch size is 5:
1. Set batch size to **7**
2. Select all 7 orders
3. Process in one batch

### Test Before Processing All

1. Enable **Test Mode**
2. Select just 1-2 orders
3. Process and verify output
4. Disable Test Mode
5. Process remaining orders

### Review Errors

1. Go to **Errors tab**
2. See which orders failed
3. Read error messages
4. Click **🔄 Retry** to try again

---

## 🚀 Deployment (Optional)

### Deploy to Streamlit Cloud (FREE)

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Deploy!
5. Access from anywhere via URL

### Run Locally

Just use:
```bash
streamlit run dashboard.py
```

No deployment needed if you're running on your own computer!

---

## 🆘 Troubleshooting

### "Connection failed" when testing Shopify

- Check your access token is correct
- Verify your store URL (should be: `46a0kn-eu.myshopify.com`)
- Ensure the token has `read_orders` permission

### "No orders found"

- Make sure you have unfulfilled orders in Shopify
- Try clicking **Refresh Orders** again
- Check your date filters aren't too restrictive

### Processing takes too long

- Claude API calls take 30-60 seconds per order
- This is normal for AI research
- Use smaller batch sizes if you want faster individual results
- Let it run in the background

### CSV not downloading

- Check your browser's download settings
- CSV is also saved to the local folder
- Look for files named `orders_*.csv`

---

## 🎨 Customization

### Change Default Batch Size

Edit line 478 in `dashboard.py`:
```python
value=5,  # Change to your preferred default
```

### Change API Credentials Defaults

Edit lines 461-475 in `dashboard.py` to update default credentials.

### Add More Filters

You can extend the date filters in the `tab1` section to add custom options.

---

## 📞 Support

If you run into issues:
1. Check the **Error Log** in the dashboard
2. Look at terminal output for detailed error messages
3. Verify API credentials are correct
4. Try with Test Mode enabled first

---

## 🎉 You're Ready!

The dashboard is fully functional and ready to use. Just run:

```bash
streamlit run dashboard.py
```

And start processing orders! 🚀
