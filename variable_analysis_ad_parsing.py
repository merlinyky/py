import pandas as pd
import re
import networkx as nx
import matplotlib.pyplot as plt
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

# Function to parse formulas with advanced parsing
def parse_formulas(formulas_str):
    dependency_graph = defaultdict(list)
    formulas = {}
    
    # Define patterns for operators and functions
    operator_pattern = r'[\+\-\*\/]'
    function_pattern = r'\b(?:lag|diff|ret)\(([^)]+)\)'
    variable_pattern = r'\b(x\d+)\b'

    for line in formulas_str.strip().split('\n'):
        parts = line.split('=')
        if len(parts) == 2:
            var, formula = parts
            # Identify dependencies by extracting variables from formulas
            variables_in_formula = re.findall(variable_pattern, formula)
            function_args = re.findall(function_pattern, formula)
            for arg in function_args:
                variables_in_formula.extend(re.findall(variable_pattern, arg))
            
            # Remove duplicates and the variable itself from dependencies
            unique_dependencies = list(set(variables_in_formula) - {var.strip()})
            dependency_graph[var.strip()] = unique_dependencies
            formulas[var.strip()] = formula.strip()

    return dependency_graph, formulas

    dependency_graph = defaultdict(list)
    formulas = {}
    
    # Define patterns for operators and functions
    operator_pattern = r'[\+\-\*\/]'
    function_pattern = r'\b(?:lag|diff|ret)\([^\)]+\)'

    for line in formulas_str.strip().split('\n'):
        parts = line.split('=')
        if len(parts) == 2:
            var, formula = parts
            # Identify dependencies by splitting based on operators and functions
            potential_vars = re.split(operator_pattern, formula)
            potential_vars = [re.sub(function_pattern, '', var) for var in potential_vars]
            dependencies = [var.strip() for var in potential_vars if var.strip() and var.strip() != var]

            dependency_graph[var.strip()] = dependencies
            formulas[var.strip()] = formula.strip()

    return dependency_graph, formulas

# Calculation functions
def lag(series, n):
    return series.shift(n)

def diff(series):
    return series.diff().abs()

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

# Function to evaluate dependencies with corrected overlay data application
def evaluate_dependencies_corrected(dependency_graph, data, formulas, overlay_data):
    calculated_values = {}
    
    def calculate_variable(var):
        if var in calculated_values:  # Already calculated
            return calculated_values[var]
        if var in overlay_data:  # Overlay data has priority
            calculated_values[var] = overlay_data[var]
            return overlay_data[var]
        if var in data:  # Base data
            return data[var]
        
        if var in formulas:
            formula = formulas[var]
            for dependency in dependency_graph[var]:
                if dependency not in calculated_values:
                    calculate_variable(dependency)

            calculated_values[var] = evaluate_formula(formula, {**data, **calculated_values})
        else:
            print(f"Formula for {var} not found")
            calculated_values[var] = pd.Series(dtype=float)

        return calculated_values[var]

    for variable in dependency_graph:
        calculate_variable(variable)
    
    return {**data, **calculated_values}

# Function to visualize the dependency graph
def visualize_dependency_graph(dependency_graph):
    G = nx.DiGraph()
    for var, deps in dependency_graph.items():
        G.add_node(var)
        for dep in deps:
            G.add_node(dep)
            G.add_edge(dep, var)

    plt.figure(figsize=(10, 6))
    pos = nx.spring_layout(G)  # This line uses spring layout
    nx.draw(G, pos, with_labels=True, node_color='lightblue', font_size=10, node_size=2000, 
            edge_color='gray', linewidths=1, font_weight='bold')
    plt.title("Dependency Graph")
    plt.show()

# Main function to run the analysis
def main(input_csv_path, formulas_txt_path, overlay_csv_path):
    input_data = read_input_data(input_csv_path)
    overlay_data = read_input_data(overlay_csv_path)
    with open(formulas_txt_path, 'r') as file:
        formulas_content = file.read()

    dependency_graph, formulas = parse_formulas(formulas_content)
    all_variable_values = evaluate_dependencies_corrected(dependency_graph, input_data, formulas, overlay_data)

    # Visualize the dependency graph
    visualize_dependency_graph(dependency_graph)

    print(dependency_graph)

    return pd.DataFrame.from_dict(all_variable_values)

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 4:
        print("Usage: python script.py <input_csv_path> <formulas_txt_path> <overlay_csv_path>")
    else:
        input_csv_path = sys.argv[1]
        formulas_txt_path = sys.argv[2]
        overlay_csv_path = sys.argv[3]
        result = main(input_csv_path, formulas_txt_path, overlay_csv_path)
        print(result)