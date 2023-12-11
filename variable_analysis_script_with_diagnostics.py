
import pandas as pd
import re
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict

# Function to read and filter input data based on the starting point
def read_and_filter_data(file_path, start_point):
    try:
        df = pd.read_csv(file_path)
        df.set_index('variable_name', inplace=True)
        # Filter the DataFrame to only include columns from start_point onwards
        filtered_df = df.loc[:, start_point:]
        return filtered_df.T.to_dict('series')
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
    return series.diff().abs()

def ret(series):
    return series.pct_change()

def evaluate_formula(formula, data):
    for var in re.findall(r'x\d+', formula):
        formula = formula.replace(var, f'data["{var}"]')
    try:
        return eval(formula)
    except KeyError as e:
        print(f"Missing data for variable: {e}")
        return pd.Series(dtype=float)
    except Exception as e:
        print(f"Error evaluating formula {formula}: {e}")
        return pd.Series(dtype=float)

# Function to evaluate dependencies
def evaluate_dependencies(dependency_graph, data, formulas, overlay_data):
    calculated_values = {}
    
    def calculate_variable(var):
        if var in data:
            return data[var]
        if var in overlay_data:
            calculated_values[var] = overlay_data[var]
            return overlay_data[var]
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

# Function to visualize the dependency graph
def visualize_dependency_graph(dependency_graph):
    G = nx.DiGraph()
    for var, deps in dependency_graph.items():
        G.add_node(var)
        for dep in deps:
            G.add_node(dep)
            G.add_edge(dep, var)

    plt.figure(figsize=(12, 8))
    nx.draw(G, with_labels=True, node_color='lightblue', font_size=10, node_size=2000, 
            edge_color='gray', linewidths=1, font_weight='bold')
    plt.title("Dependency Graph")
    plt.show()

# Main function to run the analysis
def main(input_csv_path, formulas_txt_path, overlay_csv_path, start_point):
    input_data = read_and_filter_data(input_csv_path, start_point)
    overlay_data = read_and_filter_data(overlay_csv_path, start_point)
    with open(formulas_txt_path, 'r') as file:
        formulas_content = file.read()

    dependency_graph, formulas = parse_formulas(formulas_content)
    all_variable_values = evaluate_dependencies(dependency_graph, input_data, formulas, overlay_data)

    # Visualize the dependency graph
    visualize_dependency_graph(dependency_graph)

    return pd.DataFrame.from_dict(all_variable_values)

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 5:
        print("Usage: python script.py <input_csv_path> <formulas_txt_path> <overlay_csv_path> <start_point>")
    else:
        input_csv_path = sys.argv[1]
        formulas_txt_path = sys.argv[2]
        overlay_csv_path = sys.argv[3]
        start_point = sys.argv[4]
        result = main(input_csv_path, formulas_txt_path, overlay_csv_path, start_point)
        print(result)
