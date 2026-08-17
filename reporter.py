import pandas as pd
import numpy as np
import io
from typing import Dict, Any, Tuple

def detect_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identifies and flags anomalies in the dataset:
    - Negative or zero quantities
    - Negative or zero prices
    - Outlier prices (using 1.5 * IQR method)
    
    Adds:
    - 'is_anomaly': boolean flag
    - 'anomaly_reason': string detailing why it's flagged, or empty
    """
    df = df.copy()
    df['is_anomaly'] = False
    df['anomaly_reason'] = ""
    
    reasons = []
    
    # 1. Negative/zero quantity
    if 'quantity' in df.columns:
        q_cond = df['quantity'] <= 0
        df.loc[q_cond, 'is_anomaly'] = True
        df.loc[q_cond, 'anomaly_reason'] = df.loc[q_cond, 'anomaly_reason'].apply(
            lambda x: (x + "; " if x else "") + "Non-positive Quantity"
        )
        
    # 2. Negative/zero price
    if 'price' in df.columns:
        p_cond = df['price'] <= 0
        df.loc[p_cond, 'is_anomaly'] = True
        df.loc[p_cond, 'anomaly_reason'] = df.loc[p_cond, 'anomaly_reason'].apply(
            lambda x: (x + "; " if x else "") + "Non-positive Price"
        )
        
        # 3. IQR outlier prices (calculated on positive prices to avoid skew)
        pos_prices = df.loc[df['price'] > 0, 'price']
        if len(pos_prices) > 4:
            q1 = pos_prices.quantile(0.25)
            q3 = pos_prices.quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            outlier_cond = (df['price'] > upper_bound) | (df['price'] < lower_bound)
            # Only flag as outlier if it wasn't already flagged as non-positive
            outlier_cond = outlier_cond & (df['price'] > 0)
            
            df.loc[outlier_cond, 'is_anomaly'] = True
            df.loc[outlier_cond, 'anomaly_reason'] = df.loc[outlier_cond, 'anomaly_reason'].apply(
                lambda x: (x + "; " if x else "") + f"Price Outlier (> {upper_bound:.2f} or < {lower_bound:.2f})"
            )
            
    return df

def generate_summary_report(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generates summary metrics and grouped analysis DataFrames.
    """
    report = {}
    
    # Calculate revenue if columns exist
    if 'quantity' in df.columns and 'price' in df.columns:
        df = df.copy()
        df['revenue'] = df['quantity'] * df['price']
        
        report['total_revenue'] = float(df['revenue'].sum())
        report['total_units'] = int(df['quantity'].sum())
        report['avg_unit_price'] = float(df['price'].mean())
        report['total_transactions'] = len(df)
        
        # Group by category
        if 'category' in df.columns:
            cat_summary = df.groupby('category').agg(
                total_revenue=('revenue', 'sum'),
                units_sold=('quantity', 'sum'),
                avg_price=('price', 'mean'),
                transactions=('product', 'count')
            ).reset_index()
            # Format numbers to be clean
            cat_summary['total_revenue'] = cat_summary['total_revenue'].round(2)
            cat_summary['avg_price'] = cat_summary['avg_price'].round(2)
            report['category_summary'] = cat_summary
            
        # Group by date
        date_cols = [col for col in df.columns if 'date' in col]
        if date_cols:
            date_col = date_cols[0]
            date_summary = df.groupby(date_col).agg(
                total_revenue=('revenue', 'sum'),
                units_sold=('quantity', 'sum'),
                transactions=('product', 'count')
            ).reset_index().sort_values(by=date_col)
            date_summary['total_revenue'] = date_summary['total_revenue'].round(2)
            report['date_summary'] = date_summary
            
    return report

def export_to_excel(cleaned_df: pd.DataFrame, anomalies_df: pd.DataFrame, report: Dict[str, Any]) -> io.BytesIO:
    """
    Generates an Excel workbook in memory with multiple sheets:
    - Cleaned Data
    - Anomalies
    - Summary Report (KPIs and groupings)
    """
    buffer = io.BytesIO()
    
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        # Write cleaned data
        cleaned_df.to_excel(writer, sheet_name='Cleaned Data', index=False)
        
        # Write anomalies
        anomalies_df.to_excel(writer, sheet_name='Anomalies Flagged', index=False)
        
        # Build a summary sheet manually
        summary_rows = [
            ["Metric", "Value"],
            ["Total Revenue", report.get('total_revenue', 0.0)],
            ["Total Units Sold", report.get('total_units', 0)],
            ["Average Unit Price", report.get('avg_unit_price', 0.0)],
            ["Total Transactions", report.get('total_transactions', 0)]
        ]
        summary_df = pd.DataFrame(summary_rows[1:], columns=summary_rows[0])
        summary_df.to_excel(writer, sheet_name='Summary Overview', index=False)
        
        if 'category_summary' in report:
            report['category_summary'].to_excel(writer, sheet_name='Category Breakdown', index=False)
            
        if 'date_summary' in report:
            report['date_summary'].to_excel(writer, sheet_name='Daily Breakdown', index=False)
            
    buffer.seek(0)
    return buffer
