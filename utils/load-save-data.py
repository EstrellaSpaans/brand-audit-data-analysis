def load_data(file_path, file_type='csv'):
    """
    Load dataframe from a CSV or Excel file.
    """
    if file_type == 'csv':
        return pd.read_csv(file_path)
    elif file_type == 'excel':
        return pd.read_excel(file_path)
    else:
        raise ValueError("file_type must be either 'csv' or 'excel'")

def save_data(df, filename='data', file_type='csv'):
    """
    Save DataFrame to a CSV or Excel file.
    """
    if file_type == 'csv':
        df.to_csv(f'{filename}.csv', index=False)
    elif file_type == 'excel':
        dr.to_excel(f'{filename}.xlsx', index=False)
    else:
        raise ValueError("file_type must be either 'csv' or 'excel'")
