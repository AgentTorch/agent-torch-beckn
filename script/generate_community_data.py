import pandas as pd
import numpy as np
import os
import yaml
import json
import random

# Read the configuration and data
with open('config/solar.yaml', 'r') as file:
    config = yaml.safe_load(file)

# Load price data from JSON
with open('config/data/price_data.json', 'r') as file:
    price_data = json.load(file)

# Extract the latest residential price
latest_price = None
for entry in price_data['response']['data']:
    print(entry)
    if entry["sectorName"] == "residential" and entry["price"] is not None:
        latest_price = float(entry["price"])
        break

# Check if we found a price
if latest_price is None:
    raise ValueError("No residential price found in price_data.json.")

num_communities = 144  # Total number of communities
num_grid_stations = 30  # Total number of grid stations
num_households_per_community = 20  # Households per community

# Create community directory if it doesn't exist
os.makedirs('config/data/community', exist_ok=True)

# Generate community data
community_data = []

for community_id in range(num_communities):
    # Generate household IDs for this community
    household_ids = [community_id * num_households_per_community + i for i in range(num_households_per_community)]
    
    # Create a community entry
    community_entry = {
        'community_id': community_id,
        'grid_station_id': np.random.randint(0, num_grid_stations),  # Random grid station ID
        'market_price': latest_price + random.uniform(-1, 1),  # Latest market price
        'household_ids': household_ids,  # List of household IDs
        'power_balance': 0  # Initialize power balance to 0
    }
    
    community_data.append(community_entry)

# Create DataFrames for each property and save them
df_communities = pd.DataFrame(community_data)

df_communities.to_csv('config/data/community.csv', index=False)

# Save each property in a separate CSV file
df_communities[['community_id']].to_csv('config/data/community/id.csv', index=False)
df_communities[['grid_station_id']].to_csv('config/data/community/grid_station_id.csv', index=False)
df_communities[['market_price']].to_csv('config/data/community/market_price.csv', index=False)
df_communities[['household_ids']].to_csv('config/data/community/household_ids.csv', index=False)
df_communities[['power_balance']].to_csv('config/data/community/power_balance.csv', index=False)

# Update the YAML configuration with the new community count
config['agents']['community']['count'] = num_communities

# Save the updated configuration
with open('config/solar.yaml', 'w') as file:
    yaml.dump(config, file, default_flow_style=False)

# Optionally, print the DataFrame to verify
print(df_communities.head())
