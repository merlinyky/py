import pandas as pd

def filter_dataframe(df, filter_config):
    """
    Apply filtering based on the provided configuration.
    """
    if filter_config['operation'] == '==':
        df = df[df[filter_config['column']] == filter_config['value']]
    elif filter_config['operation'] == '!=':
        df = df[df[filter_config['column']] != filter_config['value']]
    elif filter_config['operation'] == '>':
        df = df[df[filter_config['column']] > filter_config['value']]
    elif filter_config['operation'] == '<':
        df = df[df[filter_config['column']] < filter_config['value']]
    elif filter_config['operation'] == 'isin':
        df = df[df[filter_config['column']].isin(filter_config['value'])]
    return df

def groupby_and_aggregate(df, groupby_config):
    """
    Perform groupby operations and aggregations as specified in the configuration.
    """
    grouped = df.groupby(groupby_config['groupby_columns'])
    aggregated_df = grouped.agg(groupby_config['aggregations'])
    return aggregated_df

def calculate_columns(df, calculations_config):
    """
    Perform column-wise calculations as specified in the configuration using formula expressions.
    """
    for calc in calculations_config:
        if "formula" in calc:
            df[calc['new_column']] = df.eval(calc['formula'])
        else:
            if calc['operation'] == 'pct_change':
                df[calc['new_column']] = df[calc['columns'][0]].pct_change()
            # Additional operations can be added here as needed
    return df

# Sample configuration
config = {
    "filter": {
        "column": "BUSINESS",
        "operation": "==",
        "value": "Business2"
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

# Load the data
file_path = 'df_agg/df.csv'  # Replace with the path to your CSV file
df = pd.read_csv(file_path)

# Apply the configuration to the DataFrame
filtered_df = filter_dataframe(df, config['filter'])
grouped_df = groupby_and_aggregate(filtered_df, config['groupby'])
calculated_df = calculate_columns(grouped_df, config['calculations'])

# Output the processed DataFrame
print(calculated_df.head())