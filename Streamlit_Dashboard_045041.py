import pandas as pd
import streamlit as st
import altair as alt
from datetime import date

df = pd.read_csv('US_Regional_Sales_Data.csv')
df['OrderDate'] = pd.to_datetime(df['OrderDate'])

# Set the background color using a div
background_color = "#e6f7ff"  # light blue color
html_code = f"""
    <style>
        body {{
            background-color: {background_color};
        }}
    </style>
"""
st.markdown(html_code, unsafe_allow_html=True)

# Streamlit app
st.title('Sales Dashboard')

st.sidebar.header("Choose Filters: ")

date1 = pd.to_datetime(st.sidebar.date_input("Start Date", date(2018, 5, 31), min_value=date(2018, 5, 31), max_value=date(2020, 12, 20)))
date2 = pd.to_datetime(st.sidebar.date_input("End Date", date(2020, 12, 20), min_value=date(2018, 5, 31), max_value=date(2020, 12, 20)))

df = df[(df["OrderDate"] >= date1) & (df["OrderDate"] <= date2)].copy()

# Slicer for Warehouse Code with multi-select option (in the sidebar)
selected_warehouses = st.sidebar.multiselect('Select Warehouse Codes', df['WarehouseCode'].unique())

# Slicer for Sales Channel with multi-select option (in the sidebar)
selected_sales_channels = st.sidebar.multiselect('Select Sales Channels', df['SalesChannel'].unique())

# Check if filters are empty, and use the original DataFrame if they are
if not selected_warehouses and not selected_sales_channels:
    filtered_df = df.copy()
else:
    # Filter data based on selected slicer values
    filtered_df = df[(df['WarehouseCode'].isin(selected_warehouses)) &
                     (df['SalesChannel'].isin(selected_sales_channels))]

# Query 1: Warehouse Code vs. Number of Orders (Bar Graph)
st.subheader('Warehouse Code vs. Number of Orders')
warehouse_order_counts = filtered_df['WarehouseCode'].value_counts()
st.bar_chart(warehouse_order_counts)
st.text('Warehouse Code vs. Number of Orders')

# Query 2: Order Date vs. Number of Orders (Bar Graph)
st.subheader('Order Date vs. Number of Orders')
order_date_counts = filtered_df['OrderDate'].value_counts()
st.bar_chart(order_date_counts)
st.text('Order Date vs. Number of Orders')

# Query 3: Sales Channel vs. Number of Orders (Pie Chart)
st.subheader('Sales Channel vs. Number of Orders')
if 'SalesChannel' in filtered_df.columns:
    sales_channel_counts = filtered_df['SalesChannel'].value_counts().reset_index()
    sales_channel_counts.columns = ['index', 'SalesChannel']
    st.altair_chart(alt.Chart(sales_channel_counts).mark_bar().encode(
        x=alt.X('index:O', title='Sales Channel', axis=alt.Axis(labelAngle=45)),
        y=alt.Y('SalesChannel', title='Number of Orders'),
        tooltip=['index', 'SalesChannel']
    ), use_container_width=True)

# Query 4: Warehouse Code vs. Average Order Quantity (Bar Graph)
st.subheader('Warehouse Code vs. Average Order Quantity')
warehouse_avg_quantity = filtered_df.groupby('WarehouseCode')['OrderQuantity'].mean()
st.bar_chart(warehouse_avg_quantity)
st.text('Warehouse Code vs. Average Order Quantity')

# Query 5: Order Date vs. Average Order Quantity (Scatter Graph)
st.subheader('Order Date vs. Average Order Quantity')
scatter_chart = alt.Chart(filtered_df).mark_circle().encode(
    x=alt.X('OrderDate', title='Order Date'),
    y=alt.Y('mean(OrderQuantity)', title='Average Order Quantity'),
    tooltip=['OrderDate', 'mean(OrderQuantity)']
).interactive()
st.altair_chart(scatter_chart, use_container_width=True)

# Query 6: Sales Channel vs. Average Order Quantity (Bubble Chart)
st.subheader('Sales Channel vs. Average Order Quantity')
if 'SalesChannel' in filtered_df.columns:
    bubble_chart = alt.Chart(filtered_df).mark_circle().encode(
        x='SalesChannel',
        y=alt.Y('mean(OrderQuantity)', title='Average Order Quantity'),
        size='count()',
        tooltip=['SalesChannel', 'mean(OrderQuantity)', 'count()']
    ).interactive()
    st.altair_chart(bubble_chart, use_container_width=True)
else:
    st.warning("SalesChannel data not available for the selected warehouse.")
