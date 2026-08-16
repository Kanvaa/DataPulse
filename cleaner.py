import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any

def clean_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Cleans the input DataFrame:
    - Removes duplicate rows
    - Standardizes column names (lowercase, stripped)
    - Parses and formats date columns
    - Normalizes text values (strips whitespace, Title Case)
    - Imputes missing values (median for numeric, 'Unknown' for categorical)
    
    Returns the cleaned DataFrame and a dictionary of cleaning statistics.
    """
    stats = {}
    stats['initial_rows'] = len(df)
    
    # 1. Standardize column names
    df.columns = [col.strip().lower() for col in df.columns]
    
    # 2. Handle duplicates
    dup_count = df.duplicated().sum()
    df = df.drop_duplicates().reset_index(drop=True)
    stats['duplicates_removed'] = int(dup_count)
    
    # 3. Handle Dates
    # Detect date column (usually containing 'date')
    date_cols = [col for col in df.columns if 'date' in col]
    stats['date_cols_formatted'] = date_cols
    for col in date_cols:
        # Convert to datetime, coercion turns invalid parsed dates to NaT
        df[col] = pd.to_datetime(df[col], errors='coerce')
        # If any dates are NaT, we can forward fill or drop. Let's fill with today's date or drop.
        # Dropping is safer if we want high-quality reports, or we can fill with a default value.
        # Let's drop rows where date is completely missing.
        missing_dates = df[col].isna().sum()
        if missing_dates > 0:
            df = df.dropna(subset=[col]).reset_index(drop=True)
        # Format as string YYYY-MM-DD
        df[col] = df[col].dt.strftime('%Y-%m-%d')
        
    # 4. Handle text columns
    text_cols = ['product', 'category']
    for col in text_cols:
        if col in df.columns:
            # Fill missing text with 'Unknown'
            missing_text_count = df[col].isna().sum()
            df[col] = df[col].fillna('Unknown').astype(str)
            df[col] = df[col].str.strip().str.title()
            
    # 5. Handle numeric columns
    numeric_cols = ['quantity', 'price']
    stats['imputed_values'] = {}
    for col in numeric_cols:
        if col in df.columns:
            # Save count of missing
            missing_count = df[col].isna().sum()
            stats['imputed_values'][col] = int(missing_count)
            if missing_count > 0:
                # Convert to numeric
                df[col] = pd.to_numeric(df[col], errors='coerce')
                # Impute missing values with median
                median_val = df[col].median()
                if pd.isna(median_val):
                    median_val = 0.0
                df[col] = df[col].fillna(median_val)
            else:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
    stats['final_rows'] = len(df)
    return df, stats
