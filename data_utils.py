import pandas as pd
import streamlit as st
import numpy as np

@st.cache_data
def load_data():
    """
    Load the Global Retail Sales dataset from the data/ folder.
    Uses caching to avoid reloading 10,000 records on every app refresh.
    """
    file_path = "data/global_retail_sales.csv"

    try:
        # Read CSV file
        df = pd.read_csv(file_path)

        # Convert order_date to datetime for time-based analysis (drill-down by month/quarter)
        df['order_date'] = pd.to_datetime(df['order_date'])

        # Ensure all measures are numeric (handles any parsing issues)
        measures = ['quantity', 'unit_price', 'revenue', 'cost', 'profit', 'profit_margin']
        for col in measures:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        return df
    except FileNotFoundError:
        st.error(f"Dataset not found at: {file_path}. Ensure the 'data' folder contains the CSV file.")
        return None

def get_analytics_summary(df):
    """
    Generate a quick summary of key metrics for the dataset.
    Used for displaying statistics in the sidebar.
    """
    if df is not None:
        summary = {
            "Transactions": len(df),
            "Total Revenue": f"${df['revenue'].sum():,.0f}",
            "Total Profit": f"${df['profit'].sum():,.0f}",
            "Avg Margin": f"{df['profit_margin'].mean():.1%}"
        }
        return summary
    return {}

def get_data_quality_report(df):
    """
    Generate a comprehensive data quality report for the dataset.
    Includes completeness %, missing values, outliers, and type validation.
    """
    if df is None:
        return None

    report = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "completeness": {},
        "missing_values": {},
        "outliers": {},
        "type_validation": {}
    }

    # Calculate completeness and missing values for each column
    for col in df.columns:
        non_null_count = df[col].notna().sum()
        completeness_pct = (non_null_count / len(df)) * 100
        missing_count = df[col].isnull().sum()

        report["completeness"][col] = round(completeness_pct, 1)
        report["missing_values"][col] = int(missing_count)
        report["type_validation"][col] = str(df[col].dtype)

    # Detect outliers in numeric columns using z-score method (values > 3 std devs)
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df[col].notna().sum() > 0:
            mean = df[col].mean()
            std = df[col].std()
            if std > 0:
                z_scores = np.abs((df[col] - mean) / std)
                outlier_count = (z_scores > 3).sum()
                if outlier_count > 0:
                    report["outliers"][col] = int(outlier_count)

    # Calculate overall completeness
    total_cells = len(df) * len(df.columns)
    non_null_cells = df.notna().sum().sum()
    report["overall_completeness"] = round((non_null_cells / total_cells) * 100, 1)

    return report