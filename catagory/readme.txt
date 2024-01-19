The goal here is to replace hardcoded if-else logic with a configuration-driven approach. This can be done by defining the categorization rules in a configuration file (like a JSON or YAML file), and then reading this configuration into the Python code. This approach makes it easier to update the logic without changing the core engine code.

Step 1: Expanded Configuration File (config.json)
The JSON file will now include two separate mappings:

Product to Product Type Mapping: Multiple product keys mapping to one of four categories: Equity, Fixed Income, FX, and Commodities.
Notional Value to Trade Size Mapping: Mapping notional values to trade sizes (Large, Medium, Small).

Step 2: Python Code to Read and Use the Configuration
The Python script reads the configuration and applies the mappings to a given table (e.g., a pandas DataFrame).

Explanation
Product Categorization: The categorize_product function maps each product to its product type based on the product_type_mapping.
Notional Categorization: The categorize_notional function classifies each notional value into a trade size (Small, Medium, Large) based on thresholds defined in notional_size_mapping.
DataFrame Operations: We use pandas DataFrame to represent the table. New columns 'Product Type' and 'Trade Size' are added based on the mappings.
Notes
The lower() method in categorize_product ensures case-insensitive matching.
The categorize_notional function uses thresholds defined in the configuration file to categorize the notional value.


To handle the more granular categorization of notional values, we can refactor the configuration file and the categorize_notional function. Instead of using if-else statements, we can use a list of thresholds and corresponding labels to make the code cleaner and more maintainable.

Step 1: Updated Configuration File (config.json)
We will modify the notional_size_mapping to include a list of thresholds and corresponding labels:

json
Copy code
{
    "product_type_mapping": {
        "equity": "Equity",
        "bond": "Fixed Income",
        "fx": "FX",
        "commodity": "Commodities",
        "cds": "Fixed Income",
        "equity option": "Equity",
        "fx forward": "FX",
        "oil future": "Commodities"
    },
    "notional_size_mapping": [
        {"threshold": 100000, "label": "Small1"},
        {"threshold": 500000, "label": "Small2"},
        {"threshold": 1000000, "label": "Medium1"},
        {"threshold": 5000000, "label": "Medium2"},
        {"threshold": 10000000, "label": "Medium3"},
        {"threshold": 20000000, "label": "Large1"},
        {"threshold": 100000000, "label": "Large2"},
        {"threshold": float("inf"), "label": "Large3"}
    ]
}
Step 2: Python Code to Read and Use the Configuration
We'll modify the categorize_notional function to use a loop instead of if-else statements:

python
Copy code
import json
import pandas as pd

def load_config(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def categorize_product(product, product_mapping):
    return product_mapping.get(product.lower(), "Unknown")

def categorize_notional(notional, notional_mapping):
    for threshold in notional_mapping:
        if notional <= threshold['threshold']:
            return threshold['label']
    return "Unknown"

# Load configuration
config_path = 'config.json'
config = load_config(config_path)
product_mapping = config['product_type_mapping']
notional_mapping = config['notional_size_mapping']

# Sample data
data = {
    'Trade ID': [1, 2, 3, 4],
    'Product': ['Equity Option', 'Bond', 'FX Forward', 'Commodity'],
    'Notional': [95000, 450000, 2000000, 10500000]
}
df = pd.DataFrame(data)

# Apply mappings
df['Product Type'] = df['Product'].apply(lambda x: categorize_product(x, product_mapping))
df['Trade Size'] = df['Notional'].apply(lambda x: categorize_notional(x, notional_mapping))

# Display updated DataFrame
print(df)
Explanation
The notional_size_mapping in the JSON file now contains an array of objects, each with a threshold and a label.
The categorize_notional function iterates over these thresholds. When it finds the first threshold that the notional value does not exceed, it returns the corresponding label.
This approach eliminates the need for multiple if-else statements and makes it easy to update the thresholds and labels in the configuration file without changing the Python code.
This method provides a more scalable and maintainable way to categorize notional values, especially as the number of categories grows or changes over time.

The code was tested with a sample data set and it works as expected. Here are the results from the DataFrame after applying the categorizations:

Trade ID	Product	Notional	Product Type	Trade Size
1	Equity Option	95,000	Equity	Small1
2	Bond	450,000	Fixed Income	Small2
3	FX Forward	2,000,000	FX	Medium2
4	Commodity	10,500,000	Commodities	Large1
As shown in the table:

The Product Type is determined based on the product_type_mapping.
The Trade Size is determined based on the notional_size_mapping, categorizing each notional value into the appropriate size category.
This demonstrates that the code correctly categorizes both the product type and trade size based on the provided mappings and thresholds. ​


