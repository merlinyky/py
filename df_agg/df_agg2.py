# It appears the code execution environment was reset, and the previous definitions were lost.
# I will redefine the necessary functions and configurations, then test with the provided input.

import pandas as pd
import numpy as np

# Redefining the required functions

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

def is_valid_operation(column_types, operation, columns, df):
    if operation in ["+", "-", "*", "/"]:
        return all(is_numeric_type(df[col].dtype) for col in columns)
    elif operation == "pct_change":
        return len(columns) == 1 and is_numeric_type(df[columns[0]].dtype)
    return True

def calculate_columns(df, calculations_config, column_types):
    for calc in calculations_config:
        columns = calc.get("columns", [])
        operation = calc.get("operation", "")
        if not is_valid_operation(column_types, operation, columns, df):
            raise ValueError(f"Invalid operation '{operation}' for columns {columns} with types {[column_types.get(col, None) for col in columns]}")
        if "formula" in calc:
            df[calc['new_column']] = df.eval(calc['formula'])
        elif operation == 'pct_change':
            df[calc['new_column']] = df[calc['columns'][0]].pct_change()
    return df

# Configuration
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
            "new_column": "MTM_PLUS_NOTIONAL",
            "formula": "MTM + NOTIONAL"
        },
        {
            "new_column": "MTM_PCT_CHANGE",
            "operation": "pct_change",
            "columns": ["MTM"]
        }
    ]
}

# Load the provided CSV file for testing
file_path = 'df_agg/df.csv'
df_test = pd.read_csv(file_path)

# Apply the configuration to the DataFrame
try:
    filtered_df_test = filter_dataframe(df_test, config['filter'], config['column_types'])
    grouped_df_test = groupby_and_aggregate(filtered_df_test, config['groupby'], config['column_types'])
    calculated_df_test = calculate_columns(grouped_df_test, config['calculations'], config['column_types'])
    test_output = calculated_df_test.head()
except (TypeError, ValueError) as e:
    test_output = f"Error in configuration: {e}"

print(test_output)