import streamlit as st
import pandas as pd
import plotly.express as px

# Set page configuration
st.set_page_config(page_title="AWS Cloud Dashboard", layout="wide")

st.title("☁️ Cloud-Based Data Visualization Dashboard")
st.write("Upload your CSV file below to automatically analyze and visualize your data.")

# File uploader
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    # Dynamically read the CSV - no manual file changes needed
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    except UnicodeDecodeError:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, encoding='latin-1')
    
    st.markdown("### 📊 Data Preview")
    st.dataframe(df.head())
    
    st.markdown("### 📈 Comprehensive Data Visualization")
    
    # --- PERFORMANCE FIX FOR LARGE FILES ---
    row_count = len(df)
    if row_count > 5000:
        st.warning(f"⚠️ Your dataset is very large ({row_count:,} rows). To prevent the browser from crashing, the charts below are using a random sample of 5,000 rows.")
        chart_df = df.sample(n=5000, random_state=42)
    else:
        chart_df = df
    
    # Identify column types automatically
    all_columns = df.columns.tolist()
    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    categorical_columns = df.select_dtypes(exclude=['float64', 'int64']).columns.tolist()
    
    if len(numeric_columns) > 0 and len(categorical_columns) > 0:
        
        # Create tabs for better UI organization
        tab1, tab2, tab3 = st.tabs(["📊 Basic Charts", "📈 Line & Pie", "📦 Distributions"])
        
        # TAB 1: Bar & Scatter
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Bar Chart")
                x_axis = st.selectbox("Select X-Axis (Categorical)", categorical_columns, key='bar_x')
                y_axis = st.selectbox("Select Y-Axis (Numeric)", numeric_columns, key='bar_y')
                bar_fig = px.bar(chart_df, x=x_axis, y=y_axis, title=f"{y_axis} by {x_axis}")
                st.plotly_chart(bar_fig, use_container_width=True)
                
            with col2:
                st.subheader("Scatter Plot")
                if len(numeric_columns) >= 2:
                    scatter_x = st.selectbox("Select Scatter X-Axis", numeric_columns, index=0, key='scat_x')
                    scatter_y = st.selectbox("Select Scatter Y-Axis", numeric_columns, index=1, key='scat_y')
                    scatter_fig = px.scatter(chart_df, x=scatter_x, y=scatter_y, title=f"Correlation: {scatter_x} vs {scatter_y}")
                    st.plotly_chart(scatter_fig, use_container_width=True)
                else:
                    st.info("Not enough numeric columns for a scatter plot.")

        # TAB 2: Line & Pie
        with tab2:
            col3, col4 = st.columns(2)
            with col3:
                st.subheader("Line Chart")
                line_x = st.selectbox("Select Line X-Axis", all_columns, key='line_x')
                line_y = st.selectbox("Select Line Y-Axis", numeric_columns, key='line_y')
                line_fig = px.line(chart_df, x=line_x, y=line_y, title=f"Trend: {line_y} over {line_x}")
                st.plotly_chart(line_fig, use_container_width=True)
                
            with col4:
                st.subheader("Pie Chart")
                pie_names = st.selectbox("Select Categories (Names)", categorical_columns, key='pie_names')
                pie_values = st.selectbox("Select Values", numeric_columns, key='pie_values')
                pie_fig = px.pie(chart_df, names=pie_names, values=pie_values, title=f"Share of {pie_values} by {pie_names}")
                st.plotly_chart(pie_fig, use_container_width=True)

        # TAB 3: Histogram & Box Plot
        with tab3:
            col5, col6 = st.columns(2)
            with col5:
                st.subheader("Histogram")
                hist_x = st.selectbox("Select Feature for Distribution", numeric_columns, key='hist_x')
                hist_fig = px.histogram(chart_df, x=hist_x, title=f"Distribution of {hist_x}")
                st.plotly_chart(hist_fig, use_container_width=True)
                
            with col6:
                st.subheader("Box Plot")
                box_x = st.selectbox("Select Grouping (Categorical)", categorical_columns, key='box_x')
                box_y = st.selectbox("Select Value (Numeric)", numeric_columns, key='box_y')
                box_fig = px.box(chart_df, x=box_x, y=box_y, title=f"Spread of {box_y} across {box_x}")
                st.plotly_chart(box_fig, use_container_width=True)
                
    else:
        st.warning("The uploaded CSV needs at least one numeric and one text column for optimal charting.")
else:
    st.info("Awaiting CSV upload...")