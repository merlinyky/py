import pandas as pd
import numpy as np
import re

def is_numeric_type(dtype):
    return np.issubdtype(dtype, np.number)

def filter_dataframe(df, filter_config, column_types):
    column = filter_config['column']
    operation = filter_config['operation']
    if operation in ['==', '!=']:
        if not df[column].dtype == object:
            raise TypeError(f"Invalid type for operation '{operation}' on column '{column}'")
    if operation in ['>', '<']:
        if not is_numeric_type(df[column].dtype):
            raise TypeError(f"Invalid type for operation '{operation}' on column '{column}'")
    if operation == 'isin' and not isinstance(filter_config['value'], list):
        raise TypeError(f"'isin' operation requires a list of values for column '{column}'")
    if operation == '==':
        df = df[df[column] == filter_config['value']]
    elif operation == '!=':
        df = df[df[column] != filter_config['value']]
    elif operation == '>':
        df = df[df[column] > filter_config['value']]
    elif operation == '<':
        df = df[df[column] < filter_config['value']]
    elif operation == 'isin':
        df = df[df[column].isin(filter_config['value'])]
    return df

def groupby_and_aggregate(df, groupby_config, column_types):
    for column, agg_func in groupby_config['aggregations'].items():
        column_dtype = df[column].dtype
        if agg_func in ['sum', 'mean', 'median'] and not is_numeric_type(column_dtype):
            raise TypeError(f"Invalid type for aggregation '{agg_func}' on column '{column}'")
    grouped = df.groupby(groupby_config['groupby_columns'])
    aggregated_df = grouped.agg(groupby_config['aggregations'])
    return aggregated_df

def parse_formula(formula):
    function_patterns = re.findall(r'(\w+)\((\w+)\)', formula)
    for func, column in function_patterns:
        if func == 'pct_change':
            formula = formula.replace(f'{func}({column})', f'{column}.pct_change()')
        # Additional function translations can be added here
    return formula

def is_formula_valid(formula, allowed_operations):
    """
    Validates the formula by checking if it contains only allowed operations.
    """
    # Extract all words (potential function names) from the formula
    words = re.findall(r'\b\w+\b', formula)

    for word in words:
        if word not in allowed_operations and not word.isnumeric() and word not in allowed_operations:
            print(f"Disallowed operation or function: {word}")
            return False
    return True

def calculate_columns(df, calculations_config, column_types):
    allowed_operations = ["pct_change", "+", "-", "*", "/", "MTM", "NOTIONAL"]  # Include column names and operations
    for calc in calculations_config:
        if 'formula' in calc:
            formula = calc['formula']
            translated_formula = parse_formula(formula)
            if not is_formula_valid(translated_formula, allowed_operations):
                raise ValueError(f"Disallowed operation in formula: {translated_formula}")
            df[calc['new_column']] = df.eval(translated_formula)
        else:
            raise ValueError(f"Unsupported operation or missing formula in calculations: {calc}")
    return df

# Sample configuration with function-like format in calculation
config = {
    "column_types": {
        "MTM": float,
        "NOTIONAL": float,
        "BUSINESS": str,
    },
    "filter": {
        "column": "BUSINESS",
        "operation": "==",
        "value": "Business1"
    },
    "groupby": {
        "groupby_columns": ["PRODUCT"],
        "aggregations": {"MTM": "sum", "NOTIONAL": "mean"}
    },
    "calculations": [
        {
            "new_column": "COMPLEX_CALCULATION",
            "formula": "pct_change(MTM) * NOTIONAL / NOTIONAL"
        }
    ]
}

# Load the data
file_path = 'df_agg/df.csv'  # Path to the uploaded CSV file
df = pd.read_csv(file_path)

# Apply the configuration to the DataFrame
try:
    filtered_df = filter_dataframe(df, config['filter'], config['column_types'])
    grouped_df = groupby_and_aggregate(filtered_df, config['groupby'], config['column_types'])
    calculated_df = calculate_columns(grouped_df, config['calculations'], config['column_types'])
    print(calculated_df.head())
except (TypeError, ValueError) as e:
    print(f"Error in configuration: {e}")