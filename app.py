import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import random
from datetime import datetime, timedelta

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Flipkart-Style BI Dashboard", page_icon="🛒", layout="wide")
st.title("🛒 Enterprise E-Commerce Analytics")
st.markdown("Comprehensive business intelligence for category, time, pricing, and regional analysis.")

# --- 2. DATABASE & DATA GENERATION ---
def init_db():
    conn = sqlite3.connect('enterprise_sales.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_date DATE,
            category TEXT,
            price REAL,
            units_sold INTEGER,
            revenue REAL,
            location TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def generate_historical_data():
    conn = sqlite3.connect('enterprise_sales.db')
    cursor = conn.cursor()
    # Clear old data
    cursor.execute("DELETE FROM orders")
    
    categories = ["Electronics", "Fashion & Dresses", "Kitchen Appliances", "Footwear", "Toys"]
    locations = ["Andhra Pradesh", "Telangana", "Karnataka", "Maharashtra", "Tamil Nadu", "Delhi"]
    
    # Generate 1000 random orders over the last 14 months
    start_date = datetime.now() - timedelta(days=400)
    
    for _ in range(1000):
        o_date = start_date + timedelta(days=random.randint(0, 400))
        cat = random.choice(categories)
        
        # Assign realistic price ranges
        if cat == "Electronics": price = random.uniform(5000, 50000)
        elif cat == "Fashion & Dresses": price = random.uniform(500, 3000)
        elif cat == "Kitchen Appliances": price = random.uniform(1000, 8000)
        elif cat == "Footwear": price = random.uniform(400, 2500)
        else: price = random.uniform(200, 1500)
        
        units = random.randint(1, 5)
        revenue = price * units
        loc = random.choice(locations)
        
        cursor.execute("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)", 
                       (o_date.strftime('%Y-%m-%d'), cat, price, units, revenue, loc))
    
    conn.commit()
    conn.close()

# --- 3. SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("⚙️ Dashboard Controls")
    if st.button("Generate Historical Data 🔄"):
        generate_historical_data()
        st.success("1,000 Historical Orders Generated!")
        st.rerun()
    
    st.markdown("---")
    st.header("📝 Insert Manual Sale")
    with st.form("manual_entry", clear_on_submit=True):
        m_cat = st.selectbox("Category", ["Electronics", "Fashion & Dresses", "Kitchen Appliances", "Footwear", "Toys"])
        m_price = st.number_input("Unit Price (₹)", min_value=100)
        m_units = st.slider("Units Sold", 1, 10, 1)
        m_loc = st.selectbox("Location", ["Andhra Pradesh", "Telangana", "Karnataka", "Maharashtra", "Tamil Nadu", "Delhi"])
        if st.form_submit_button("Log Order"):
            conn = sqlite3.connect('enterprise_sales.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)", 
                           (datetime.now().strftime('%Y-%m-%d'), m_cat, m_price, m_units, m_price*m_units, m_loc))
            conn.commit()
            conn.close()
            st.success("Order Logged!")
            st.rerun()

# --- 4. DATA FETCHING & PROCESSING ---
def get_data():
    conn = sqlite3.connect('enterprise_sales.db')
    df = pd.read_sql_query("SELECT * FROM orders ORDER BY order_date ASC", conn)
    conn.close()
    if not df.empty:
        df['order_date'] = pd.to_datetime(df['order_date'])
        df['Month_Year'] = df['order_date'].dt.to_period('M').astype(str)
        df['Year'] = df['order_date'].dt.year.astype(str)
    return df

df = get_data()

# --- 5. VISUALIZATION DASHBOARD ---
if len(df) > 0:
    # Top Level KPIs
    total_rev = df['revenue'].sum()
    total_orders = len(df)
    top_loc = df.groupby('location')['revenue'].sum().idxmax()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Platform Revenue", f"₹{total_rev:,.0f}")
    c2.metric("Total Orders Processed", f"{total_orders:,}")
    c3.metric("Highest Performing Region", top_loc)
    
    st.markdown("---")
    
    # Create organizational tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Category Analysis", "📈 Time & Sales Trends", "💰 Price vs. Demand", "📍 Regional Sales"])
    
    with tab1:
        st.subheader("Revenue by Product Category")
        cat_df = df.groupby('category')['revenue'].sum().reset_index()
        fig_cat = px.bar(cat_df, x='category', y='revenue', color='category', template="plotly_dark")
        st.plotly_chart(fig_cat, width="stretch")
        
    with tab2:
        st.subheader("Monthly Revenue Trends (Year-over-Year)")
        monthly_df = df.groupby('Month_Year')['revenue'].sum().reset_index()
        fig_time = px.line(monthly_df, x='Month_Year', y='revenue', markers=True, template="plotly_dark")
        fig_time.update_traces(line_color='#00FFAA')
        st.plotly_chart(fig_time, width="stretch")
        
    with tab3:
        st.subheader("Does increasing price decrease sales volume?")
        # Scatter plot to show correlation between price and units sold
        fig_price = px.scatter(df, x="price", y="units_sold", color="category", size="revenue", 
                               hover_data=['category'], template="plotly_dark", opacity=0.7)
        st.plotly_chart(fig_price, width="stretch")
        st.info("💡 Analysis: Typically, lower-priced items (left side) should have higher units sold (top side). High-priced electronics will cluster at the bottom right.")
        
    with tab4:
        st.subheader("Sales Distribution by Location")
        loc_df = df.groupby('location')['revenue'].sum().reset_index().sort_values(by='revenue', ascending=True)
        # Horizontal bar chart for clean geographical representation
        fig_loc = px.bar(loc_df, x='revenue', y='location', orientation='h', color='revenue', color_continuous_scale="Viridis", template="plotly_dark")
        st.plotly_chart(fig_loc, width="stretch")

else:
    st.warning("Database empty. Click 'Generate Historical Data' in the sidebar to populate the dashboard.")