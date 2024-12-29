import pandas as pd
import numpy as np
import os
import yaml

# Read the configuration and data
with open('config/solar.yaml', 'r') as file:
    config = yaml.safe_load(file)

df = pd.read_csv('config/data/energy_data.csv')

# Filter for electric energy only
df_electric = df[df['energy_type'] == 'Electric']

# Get unique households
unique_households = df_electric[['street_address', 'latitude', 'longitude']].drop_duplicates().sort_values(by=['latitude', 'longitude']).reset_index()
num_households = len(unique_households)

# Create household directory if it doesn't exist
os.makedirs('config/data/household', exist_ok=True)

# Process each property defined in the YAML
def generate_synthetic_data(property_name, num_households):
    if property_name == 'id':
        return pd.DataFrame({'id': range(num_households)})
    
    elif property_name == 'community_id':
        # Create community IDs such that each community has exactly 20 households
        community_ids = np.repeat(range(144), 20)  # 144 communities, 20 households each
        return pd.DataFrame({'community_id': community_ids})
    
    elif property_name == 'location':
        return unique_households[['latitude', 'longitude']]
    
    elif property_name == 'demand_profile':
        demand_profiles = []
        for _, house in unique_households.iterrows():
            house_demand = df_electric[df_electric['street_address'] == house['street_address']]
            demand_profiles.append(house_demand.sort_values('month')['energy_demand'].values)
        return pd.DataFrame(demand_profiles)
    
    elif property_name == 'has_solar':
        # Initially no one has solar
        return pd.DataFrame({'has_solar': [False] * num_households})
    
    elif property_name == 'generation_capacity':
        # Initialize with zeros (12 months)
        return pd.DataFrame(np.zeros((num_households, 12)))
    
    elif property_name == 'battery_capacity':
        # Define possible battery capacities
        capacities = [0, 5, 5, 15, 15, 13.5, 15, 50, 50, 50, 50, 100, 100, 100, 15, 10, 10]
        # Randomly select from these capacities for each household
        return pd.DataFrame({'battery_capacity': np.random.choice(capacities, num_households)})
    
    elif property_name == 'battery_charge':
        # Initialize all batteries with 0 charge
        return pd.DataFrame({'battery_charge': [0.0] * num_households})
    
    elif property_name == 'excess_energy':
        # Start with no excess energy
        return pd.DataFrame({'excess_energy': [0.0] * num_households})
    
    elif property_name == 'financial_capacity':
        # Random financial capacity between $10,000 and $100,000
        return pd.DataFrame({'financial_capacity': np.random.uniform(10000, 100000, num_households)})
    
    elif property_name == 'adoption_propensity':
        # Random propensity between 0 and 1
        return pd.DataFrame({'adoption_propensity': np.random.uniform(0, 1, num_households)})
    
    elif property_name == 'neighbor_adoption':
        # Initialize with all False (10 neighbors)
        return pd.DataFrame(np.zeros((num_households, 10), dtype=bool))
    
    elif property_name == 'expected_roi':
        # Initialize with random ROI expectations between 5-15%
        return pd.DataFrame({'expected_roi': np.random.uniform(0.05, 0.15, num_households)})
    
    elif property_name == 'grid_consumption':
        # Initialize with current demand as grid consumption
        return pd.DataFrame({'grid_consumption': df_electric.groupby('street_address')['energy_demand'].mean().values})

# Generate and save all properties
for prop_name in config['agents']['household']['properties']:
    df_prop = generate_synthetic_data(prop_name, num_households)
    df_prop.to_csv(f'config/data/household/{prop_name}.csv', index=False)

# Update the YAML configuration with the new household count
config['agents']['household']['count'] = num_households

# Save the updated configuration
with open('config/solar.yaml', 'w') as file:
    yaml.dump(config, file, default_flow_style=False)
