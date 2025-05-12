
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

    # Use 'Submission Date' if it exists and has valid entries, otherwise use 'Date'
    if 'Submission Date' in df.columns and df['Submission Date'].notna().sum() > 0:
        df['Parsed Date'] = pd.to_datetime(df['Submission Date'], errors='coerce')
    else:
        df['Parsed Date'] = pd.to_datetime(df['Date'], errors='coerce')

    # Extract month and tech
    df['Month'] = df['Parsed Date'].dt.strftime('%Y-%m')
    df['Tech'] = df['Tech'].astype(str)

    # Drop rows with no Parsed Date
    df = df[df['Parsed Date'].notna()]

    # Sidebar filters only after parsing
    st.sidebar.header("Filters")
    unique_techs = df['Tech'].dropna().unique()
    unique_months = df['Month'].dropna().unique()

    tech_filter = st.sidebar.multiselect("Select Tech(s)", options=sorted(unique_techs), default=sorted(unique_techs))
    month_filter = st.sidebar.multiselect("Select Month(s)", options=sorted(unique_months), default=sorted(unique_months))

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
    if not monthly_chart.empty:
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.barplot(data=monthly_chart, x='Month', y='Survey Count', hue='Tech', ax=ax)
        ax.set_title("Surveys per Tech by Month")
        ax.set_xlabel("Month")
        ax.set_ylabel("Survey Count")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
        fig.tight_layout()
        st.pyplot(fig)
    else:
        st.warning("No data available for the selected filters.")
