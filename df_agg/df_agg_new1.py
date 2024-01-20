import pandas as pd
from typing import Dict

def filter_and_calculate(df: pd.DataFrame, formula: Dict[str, Dict[str, str]]) -> pd.DataFrame:
    """
    Apply filtering and calculation conditions defined in the formula to the DataFrame.

    :param df: Pandas DataFrame to filter and calculate.
    :param formula: Dictionary containing the filter conditions and calculations.
    :return: DataFrame after applying filter and calculation.
    """
    for condition, calculations in formula.items():
        # Fixing the condition string for correct syntax
        condition_fixed = condition.replace("AND", "and").replace("OR", "or")
        filtered_df = df.query(condition_fixed)

        filtered_df = apply_calculations(filtered_df, calculations)
        df = filtered_df
    return df

def apply_calculations(df: pd.DataFrame, calculations: Dict[str, str]) -> pd.DataFrame:
    """
    Apply calculations to create new columns in the DataFrame.

    This function handles both simple arithmetic operations and special method calls (like pct_change).

    :param df: Pandas DataFrame to perform calculations on.
    :param calculations: Dictionary of new column names and their calculation formulas.
    :return: DataFrame with new columns.
    """
    for new_col, formula in calculations.items():
        if 'pct_change' in formula:
            # Extracting the column name for pct_change and the rest of the formula
            pct_col = formula.split('(')[1].split(')')[0]
            remaining_formula = formula.split(')')[1].strip()
            df[new_col] = df[pct_col].pct_change()
            if remaining_formula:
                # Apply the remaining part of the formula if it exists
                df[new_col] = df.eval(f"{new_col}{remaining_formula}")
        else:
            # For simple arithmetic operations
            df[new_col] = df.eval(formula)
    return df

# Loading the data from CSV
df_path = 'df_agg/df.csv'  # Replace with your CSV file path
df = pd.read_csv(df_path)

# JSON configuration embedded directly in the code
config = {
    "formula": {
        "BUSINESS == 'Business1' AND PRODUCT == 'equity'": {
            "CALCULATION": "pct_change(MTM) * NOTIONAL / 1000"
        }
    }
}

# Applying the filter and calculation as per the 'formula' in the configuration
formula_config = config.get('formula', {})
result_df = filter_and_calculate(df, formula_config)

# Display the resulting DataFrame
print(result_df.head())
