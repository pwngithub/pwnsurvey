
import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("FTTH Survey Summary by Tech")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx", "xlsm"])
if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name=0)

    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Month'] = df['Date'].dt.strftime('%Y-%m')
    df['Day'] = df['Date'].dt.date
    df['Tech'] = df['Tech'].astype(str)

    # Sidebar filters
    st.sidebar.header("Filters")
    tech_filter = st.sidebar.multiselect("Select Tech(s)", df['Tech'].dropna().unique(), default=df['Tech'].dropna().unique())
    month_filter = st.sidebar.multiselect("Select Month(s)", df['Month'].dropna().unique(), default=df['Month'].dropna().unique())
    day_filter = st.sidebar.multiselect("Select Day(s)", df['Day'].dropna().unique(), default=df['Day'].dropna().unique())

    # Apply filters
    filtered_df = df[
        (df['Tech'].isin(tech_filter)) &
        (df['Month'].isin(month_filter)) &
        (df['Day'].isin(day_filter))
    ]

    st.subheader("Survey Counts by Tech")
    summary = filtered_df.groupby('Tech').size().reset_index(name='Survey Count')
    st.dataframe(summary)
