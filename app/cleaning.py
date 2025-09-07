import pandas as pd
from io import BytesIO

def read_dataframe(file_obj, filename):
    if filename.lower().endswith(('.xls', '.xlsx')):
        return pd.read_excel(file_obj)
    return pd.read_csv(file_obj)

def clean_dataframe(df, options):
    # Remove duplicates
    if options.get('remove_duplicates', True):
        df = df.drop_duplicates()
    
    # Trim whitespace
    if options.get('trim_whitespace', True):
        df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
    
    # Fill missing values
    fill_mode = options.get('fill_missing', '')
    if fill_mode == 'mean':
        df = df.fillna(df.mean(numeric_only=True))
    elif fill_mode == 'median':
        df = df.fillna(df.median(numeric_only=True))
    elif fill_mode == 'custom':
        custom_value = options.get('custom_value', '')
        df = df.fillna(custom_value)
    
    # Rename columns
    rename_map = options.get('rename_map', {})
    if rename_map:
        df = df.rename(columns=rename_map)
    
    return df

def process_file(file_obj, filename, options):
    df = read_dataframe(file_obj, filename)
    original_rows = len(df)
    
    df = clean_dataframe(df, options)
    cleaned_rows = len(df)
    
    # Convert to Excel in memory
    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    
    return output, original_rows, cleaned_rows