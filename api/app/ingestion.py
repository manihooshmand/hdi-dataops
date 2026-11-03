import pandas as pd

def transform_wide_to_long(df: pd.DataFrame) -> list[dict]:
    # Identify year columns dynamically
    id_vars = ['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code']
    year_cols = [col for col in df.columns if col.isdigit()]
    
    # Melt wide format to long format
    melted_df = pd.melt(df, id_vars=id_vars, value_vars=year_cols, var_name='year', value_name='value')
    
    # Clean data types and drop empty values
    melted_df['year'] = pd.to_numeric(melted_df['year'], errors='coerce')
    melted_df['value'] = pd.to_numeric(melted_df['value'], errors='coerce')
    melted_df.dropna(subset=['value'], inplace=True)
    
    # Select and rename required columns
    result_df = melted_df[['Country Code', 'Indicator Code', 'year', 'value']]
    result_df.rename(columns={'Country Code': 'country_code', 'Indicator Code': 'indicator_code'}, inplace=True)
    
    return result_df.to_dict(orient='records')