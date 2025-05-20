
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from dateutil import parser
import os

st.set_page_config(layout="wide")
st.title("FTTH Survey Summary by Tech")

SHARED_DIR = "shared_uploads"
os.makedirs(SHARED_DIR, exist_ok=True)

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx", "xlsm"])
if uploaded_file:
    # Save uploaded file to shared directory
    save_path = os.path.join(SHARED_DIR, uploaded_file.name)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"File saved to {save_path} for shared use.")

    df = pd.read_excel(uploaded_file, sheet_name=0)
    df.columns = df.columns.str.strip()

    # Parse Submission Date
    if 'Submission Date' in df.columns:
        df['Parsed Date'] = df['Submission Date'].apply(
            lambda x: parser.parse(str(x), fuzzy=True) if pd.notnull(x) else pd.NaT
        )
    else:
        df['Parsed Date'] = pd.to_datetime(df['Date'], errors='coerce')

    df['Month'] = df['Parsed Date'].dt.strftime('%Y-%m')
    df['Tech'] = df['Tech'].astype(str)
    df = df[df['Parsed Date'].notna()]

    # Sidebar filters
    st.sidebar.header("Filters")
    tech_filter = st.sidebar.multiselect("Select Tech(s)", options=sorted(df['Tech'].unique()), default=sorted(df['Tech'].unique()))
    month_filter = st.sidebar.multiselect("Select Month(s)", options=sorted(df['Month'].unique()), default=sorted(df['Month'].unique()))

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
