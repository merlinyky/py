
import pandas as pd
import re
from collections import defaultdict

# Function to read input data
def read_input_data(file_path):
    try:
        df = pd.read_csv(file_path)
        df.set_index('variable_name', inplace=True)
        return df.T.to_dict('series')
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None

# Function to parse formulas
def parse_formulas(formulas_str):
    dependency_graph = defaultdict(list)
    formulas = {}
    
    for line in formulas_str.strip().split('\n'):
        parts = line.split('=')
        if len(parts) == 2:
            var, formula = parts
            dependencies = re.findall(r'x\d+', formula)
            dependency_graph[var.strip()] = dependencies
            formulas[var.strip()] = formula.strip()

    return dependency_graph, formulas

# Calculation functions
def lag(series, n):
    return series.shift(n)

def diff(series):
    return series.diff()

def ret(series):
    return series.pct_change()

def evaluate_formula(formula, data):
    for var in re.findall(r'x\d+', formula):
        formula = formula.replace(var, f'data["{var}"]')
    try:
        return eval(formula)
    except Exception as e:
        print(f"Error evaluating formula {formula}: {e}")
        return None

# Function to evaluate dependencies
def evaluate_dependencies(dependency_graph, data, formulas):
    calculated_values = {}
    
    def calculate_variable(var):
        if var in data:
            return data[var]
        if var in calculated_values:
            return calculated_values[var]
        
        formula = formulas[var]
        for dependency in dependency_graph[var]:
            if dependency not in calculated_values:
                calculate_variable(dependency)

        calculated_values[var] = evaluate_formula(formula, {**data, **calculated_values})
        return calculated_values[var]

    for variable in dependency_graph:
        calculate_variable(variable)
    
    return {**data, **calculated_values}

# Main function to run the analysis
def main(input_csv_path, formulas_txt_path):
    input_data = read_input_data(input_csv_path)
    with open(formulas_txt_path, 'r') as file:
        formulas_content = file.read()

    dependency_graph, formulas = parse_formulas(formulas_content)
    all_variable_values = evaluate_dependencies(dependency_graph, input_data, formulas)

    return pd.DataFrame.from_dict(all_variable_values)

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python script.py <input_csv_path> <formulas_txt_path>")
    else:
        input_csv_path = sys.argv[1]
        formulas_txt_path = sys.argv[2]
        result = main(input_csv_path, formulas_txt_path)
        print(result)
