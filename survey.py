
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("FTTH Survey Summary by Tech")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx", "xlsm"])
if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name=0)

    df.columns = df.columns.str.strip()
    df['Submission Date'] = pd.to_datetime(df['Submission Date'], errors='coerce')
    df['Month'] = df['Submission Date'].dt.strftime('%Y-%m')
    df['Tech'] = df['Tech'].astype(str)

    # Sidebar filters
    st.sidebar.header("Filters")
    tech_filter = st.sidebar.multiselect("Select Tech(s)", df['Tech'].dropna().unique(), default=df['Tech'].dropna().unique())
    month_filter = st.sidebar.multiselect("Select Month(s)", df['Month'].dropna().unique(), default=df['Month'].dropna().unique())

    # Apply filters
    filtered_df = df[
        (df['Tech'].isin(tech_filter)) &
        (df['Month'].isin(month_filter))
    ]

    st.subheader("Survey Counts by Tech")
    summary = filtered_df.groupby('Tech').size().reset_index(name='Survey Count')
    st.dataframe(summary)

    st.subheader("Monthly Survey Totals by Tech (Chart)")
    monthly_chart = filtered_df.groupby(['Month', 'Tech']).size().reset_index(name='Survey Count')
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=monthly_chart, x='Month', y='Survey Count', hue='Tech', ax=ax)
    ax.set_title("Surveys per Tech by Month")
    ax.set_xlabel("Month")
    ax.set_ylabel("Survey Count")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    fig.tight_layout()
    st.pyplot(fig)
