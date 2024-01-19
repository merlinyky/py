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
config_path = "mapping.json"
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