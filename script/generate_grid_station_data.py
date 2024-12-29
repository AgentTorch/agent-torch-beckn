import pandas as pd
import numpy as np
import os
import yaml
import json

# Read the configuration and data
with open('config/solar.yaml', 'r') as file:
    config = yaml.safe_load(file)

# Load community data
df_communities = pd.read_csv('config/data/community.csv')

num_grid_stations = 30  # Total number of grid stations

# Create grid station directory if it doesn't exist
os.makedirs('config/data/grid_station', exist_ok=True)

# Generate grid station data
grid_station_data = []

# Group communities by grid station ID
grouped_communities = df_communities.groupby('grid_station_id')

for grid_station_id in range(num_grid_stations):
    # Get communities associated with this grid station
    communities = grouped_communities.get_group(grid_station_id) if grid_station_id in grouped_communities.groups else pd.DataFrame()
    
    # Get community IDs
    community_ids = communities['community_id'].tolist()
    
    # Calculate average market price for the communities
    if not communities.empty:
        average_market_price = communities['market_price'].mean()
    else:
        average_market_price = 0  # Default if no communities are associated
    
    # Generate max capacity randomly (e.g., between 1000 kW and 15000 kW)
    max_capacity = np.random.uniform(1000, 15000)
    
    # Generate reliability randomly (e.g., between 0.85 and 1.0)
    reliability = np.random.uniform(0.85, 1.0)
    
    # Create a grid station entry
    grid_station_entry = {
        'grid_station_id': grid_station_id,
        'community_ids': community_ids,  # List of community IDs
        'current_load': 0,  # Set current load to half of max capacity
        'dynamic_price': average_market_price,  # Set dynamic price to average market price
        'max_capacity': max_capacity,  # Randomly generated max capacity
        'reliability': reliability  # Randomly generated reliability
    }
    
    grid_station_data.append(grid_station_entry)

# Create a DataFrame from the grid station data
df_grid_stations = pd.DataFrame(grid_station_data)

# Save each property in a separate CSV file
df_grid_stations[['grid_station_id']].to_csv('config/data/grid_station/id.csv', index=False)
df_grid_stations[['community_ids']].to_csv('config/data/grid_station/community_ids.csv', index=False)
df_grid_stations[['current_load']].to_csv('config/data/grid_station/current_load.csv', index=False)
df_grid_stations[['dynamic_price']].to_csv('config/data/grid_station/dynamic_price.csv', index=False)
df_grid_stations[['max_capacity']].to_csv('config/data/grid_station/max_capacity.csv', index=False)
df_grid_stations[['reliability']].to_csv('config/data/grid_station/reliability.csv', index=False)

# Optionally, print the DataFrame to verify
print(df_grid_stations.head())
