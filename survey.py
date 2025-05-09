
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("FTTH Survey Dashboard")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx", "xlsm"])
if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name=0)

    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Drop Length (ft)'] = df['What is the Measuring Wheel footage?'].astype(str).str.extract(r'(\d+)').astype(float)
    df['Prep Hours'] = df['How many hours will the prep take?'].astype(str).str.extract(r'(\d+\.?\d*)').astype(float)

    df['Month'] = df['Date'].dt.to_period('M').astype(str)
    df['Year'] = df['Date'].dt.year
    df['Day'] = df['Date'].dt.date

    # Sidebar filters
    st.sidebar.header("Filters")
    tech_filter = st.sidebar.multiselect("Select Tech(s)", options=df['Tech'].dropna().unique(), default=df['Tech'].dropna().unique())
    date_range = st.sidebar.date_input("Select Date Range", value=(df['Date'].min(), df['Date'].max()))
    drop_min, drop_max = st.sidebar.slider("Drop Length (ft)", float(df['Drop Length (ft)'].min(skipna=True)), float(df['Drop Length (ft)'].max(skipna=True)), (float(df['Drop Length (ft)'].min(skipna=True)), float(df['Drop Length (ft)'].max(skipna=True))))
    prep_min, prep_max = st.sidebar.slider("Prep Hours", float(df['Prep Hours'].min(skipna=True)), float(df['Prep Hours'].max(skipna=True)), (float(df['Prep Hours'].min(skipna=True)), float(df['Prep Hours'].max(skipna=True))))

    # Apply filters
    filtered_df = df[
        (df['Tech'].isin(tech_filter)) &
        (df['Date'] >= pd.to_datetime(date_range[0])) &
        (df['Date'] <= pd.to_datetime(date_range[1])) &
        (df['Drop Length (ft)'].between(drop_min, drop_max)) &
        (df['Prep Hours'].between(prep_min, prep_max))
    ]

    st.subheader("Filtered Survey Data")
    st.dataframe(filtered_df)

    # Visuals
    st.subheader("Job Count by Tech")
    tech_counts = filtered_df['Tech'].value_counts().reset_index()
    tech_counts.columns = ['Tech', 'Count']
    fig1, ax1 = plt.subplots()
    sns.barplot(data=tech_counts, x='Tech', y='Count', ax=ax1)
    ax1.set_title("Number of Jobs per Tech")
    st.pyplot(fig1)

    st.subheader("Jobs Over Time")
    daily_counts = filtered_df.groupby('Date').size().reset_index(name='Job Count')
    fig2, ax2 = plt.subplots()
    sns.lineplot(data=daily_counts, x='Date', y='Job Count', marker='o', ax=ax2)
    ax2.set_title("Jobs Over Time")
    st.pyplot(fig2)

    st.subheader("Tech Jobs Per Day")
    tech_per_day = filtered_df.groupby(['Tech', 'Day']).size().reset_index(name='Jobs Per Day')
    fig_day, ax_day = plt.subplots(figsize=(10, 5))
    sns.lineplot(data=tech_per_day, x='Day', y='Jobs Per Day', hue='Tech', marker='o', ax=ax_day)
    ax_day.set_title("Tech Jobs Per Day")
    ax_day.tick_params(axis='x', rotation=45)
    st.pyplot(fig_day)

    st.subheader("Tech Jobs Per Month (Stacked Bar)")
    tech_per_month = filtered_df.groupby(['Tech', 'Month']).size().reset_index(name='Jobs Per Month')
    pivot_month = tech_per_month.pivot(index='Month', columns='Tech', values='Jobs Per Month').fillna(0)
    fig_month, ax_month = plt.subplots(figsize=(12, 6))
    pivot_month.plot(kind='bar', stacked=True, ax=ax_month)
    ax_month.set_title("Tech Jobs Per Month (Stacked)")
    ax_month.set_ylabel("Job Count")
    ax_month.set_xlabel("Month")
    ax_month.legend(title="Tech", bbox_to_anchor=(1.05, 1), loc='upper left')
    st.pyplot(fig_month)

    st.subheader("Tech Jobs Per Year")
    tech_per_year = filtered_df.groupby(['Tech', 'Year']).size().reset_index(name='Jobs Per Year')
    fig_year, ax_year = plt.subplots()
    sns.barplot(data=tech_per_year, x='Year', y='Jobs Per Year', hue='Tech', ax=ax_year)
    ax_year.set_title("Jobs Per Year per Tech")
    st.pyplot(fig_year)

    st.subheader("Tech Jobs Per Month Table & Heatmap")
    summary_table = tech_per_month.pivot(index='Tech', columns='Month', values='Jobs Per Month').fillna(0).astype(int)
    st.dataframe(summary_table)

    fig_heatmap, ax_heatmap = plt.subplots(figsize=(12, 6))
    sns.heatmap(summary_table, annot=True, fmt="d", cmap="YlGnBu", linewidths=0.5, linecolor='gray', ax=ax_heatmap)
    ax_heatmap.set_title("Jobs Per Month per Tech (Heatmap Style)")
    st.pyplot(fig_heatmap)
