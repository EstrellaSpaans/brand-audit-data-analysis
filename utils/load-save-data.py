def load_brands_data(file_path, file_type='csv'):
    """
    Load brands data from a CSV or Excel file.
    """
    if file_type == 'csv':
        return pd.read_csv(file_path)
    elif file_type == 'excel':
        return pd.read_excel(file_path)
    else:
        raise ValueError("file_type must be either 'csv' or 'excel'")

def save_brands_data(brands, filename='general_brand_data', file_type='csv'):
    """
    Save brands DataFrame to a CSV or Excel file.
    """
    if file_type == 'csv':
        brands.to_csv(f'{filename}.csv', index=False)
    elif file_type == 'excel':
        brands.to_excel(f'{filename}.xlsx', index=False)
    else:
        raise ValueError("file_type must be either 'csv' or 'excel'")
