# ---------------------------------------------------------
# metrics.py
# ---------------------------------------------------------

import torch

from rich.console import Console
from rich.tree import Tree

from utilities import format_tensor

# Helper function to get data from nested state dict
def get_agent_data(state, agent_type, field):
    return state['agents'][agent_type][field]

# ----- 3.1 Energy Self-Sufficiency Metrics -----

# 3.1.1 Community Self-Sufficiency Ratio (CSR)
def calculate_csr(state):
    communities = get_agent_data(state, 'community', 'id')
    power_balance = get_agent_data(state, 'community', 'power_balance')
    household_ids = get_agent_data(state, 'community', 'household_ids')
    demand_profile = get_agent_data(state, 'household', 'demand_profile')
    
    csr_values = {}
    for c_id in range(len(communities)):
        valid_households = household_ids[c_id][household_ids[c_id] > 0] - 1
        
        community_demand = torch.sum(demand_profile[valid_households])
        grid_imports = torch.clamp(-1 * power_balance[c_id], min=0)
        
        # Calculate csr
        csr = 1 - (grid_imports / community_demand) if community_demand > 0 else torch.tensor(0.0)
        csr_values[f'community_{c_id}'] = csr.item()

    return csr_values

# 3.1.2 Peak Import Reduction (PIR)
def calculate_pir(state):
    grid_load = get_agent_data(state, 'grid_station', 'current_load')
    max_capacity = get_agent_data(state, 'grid_station', 'max_capacity')
    
    peak_imports = torch.max(grid_load, dim=0).values
    pir = 1 - (peak_imports / max_capacity)
    
    return {f'grid_{i}': pir[i].item() for i in range(len(pir))}

# 3.1.3 Storage Utilization Factor (SUF)
def calculate_suf(state):
    battery_charge = get_agent_data(state, 'household', 'battery_charge')
    battery_capacity = get_agent_data(state, 'household', 'battery_capacity')
    community_ids = get_agent_data(state, 'household', 'community_id')
    
    suf_values = {}
    unique_communities = torch.unique(community_ids)
    
    for comm in unique_communities:
        comm_mask = community_ids == comm
        comm_charge = battery_charge[comm_mask]
        comm_capacity = battery_capacity[comm_mask]
        
        # Calculate average utilization
        suf = torch.mean(comm_charge / comm_capacity) if comm_capacity.sum() > 0 else 0
        suf_values[f'community_{comm.item()}'] = suf.item()
        
    return suf_values

# ----- 3.2 Solar Adoption Metrics -----

# 3.2.1 Solar Penetration Rate (SPR)
def calculate_spr(state):
    has_solar = get_agent_data(state, 'household', 'has_solar')
    community_ids = get_agent_data(state, 'household', 'community_id')
    
    spr_values = {}
    unique_communities = torch.unique(community_ids)
    
    for comm in unique_communities:
        comm_mask = community_ids == comm
        solar_count = torch.sum(has_solar[comm_mask].float())
        total_households = torch.sum(comm_mask.float())
        
        spr = solar_count / total_households if total_households > 0 else 0
        spr_values[f'community_{comm.item()}'] = spr.item()
        
    return spr_values

# 3.2.2 Solar Investment Return (SIR)
def calculate_sir(state):
    has_solar = get_agent_data(state, 'household', 'has_solar')
    generation_capacity = get_agent_data(state, 'household', 'generation_capacity')
    financial_capacity = get_agent_data(state, 'household', 'financial_capacity')
    installation_cost = state['environment']['installation_cost']
    
    solar_mask = has_solar == 1
    grid_price = state['environment']['grid_price']
    annual_generation = generation_capacity.squeeze().sum()
    annual_revenue = annual_generation * grid_price
    
    sir = torch.where(
        solar_mask,
        annual_revenue / installation_cost if installation_cost > 0 else 0,
        torch.zeros_like(annual_revenue)
    )
    
    adopters_count = torch.sum(solar_mask.float())
    successful_count = torch.sum((sir >= 1.5).float() * solar_mask.float())
    success_rate = successful_count / adopters_count if adopters_count > 0 else 0
    
    return {
        'average_sir': torch.mean(sir[solar_mask]).item() if torch.sum(solar_mask) > 0 else 0,
        'success_rate': success_rate
    }

# ----- 3.3 Market Efficiency Metrics -----

# 3.3.1 Price Stability Index (PSI)
def calculate_psi(state):
    market_price = get_agent_data(state, 'community', 'market_price')
    
    psi_values = {}
    for i in range(len(market_price)):
        mean_price = torch.mean(market_price[i])
        std_price = torch.std(market_price[i])
        psi = std_price / mean_price
        psi_values[f'community_{i}'] = psi.item()
        
    return psi_values

# 3.3.2 Trading Volume Ratio (TVR)
def calculate_tvr(state):
    excess_energy = get_agent_data(state, 'household', 'excess_energy')
    demand_profile = get_agent_data(state, 'household', 'demand_profile')
    community_ids = get_agent_data(state, 'household', 'community_id')
    
    tvr_values = {}
    unique_communities = torch.unique(community_ids)
    demand_profile = demand_profile.sum(1)
    
    for comm in unique_communities:
        comm_mask = community_ids == comm
        
        # Calculate total trading volume and demand
        trading_volume = torch.sum(excess_energy[comm_mask])
        total_demand = torch.sum(demand_profile[comm_mask.squeeze()])
        
        tvr = trading_volume / total_demand
        tvr_values[f'community_{comm.item()}'] = tvr.item()
        
    return tvr_values


def calculate_metrics(state):
    """
    Calculates all performance metrics for the solar network model.
    
    Args:
        state (dict): Current state of the simulation containing all agent and environment variables
        
    Returns:
        dict: Dictionary containing all calculated metrics
    """
    
    # Calculate all metrics
    csr = calculate_csr(state); pir = calculate_pir(state); suf = calculate_suf(state)
    spr = calculate_spr(state); sir = calculate_sir(state); psi = calculate_psi(state)
    tvr = calculate_tvr(state)

    # Store them in a dict
    metrics = {
      '(csr) community self sufficiency ratio': {}, # csr,
      '(pir) peak import reduction': {}, # pir,
      '(suf) storage utilization factor': {}, # suf,
      '(spf) solar penetration factor': {}, # spr,
      '(sir) solar investment returns': {}, # sir,
      '(psi) price stability index': {}, # psi,
      '(tvr) trading volume ratio': {}, # tvr,
    }
    
    # Add overall performance indicators
    for metric, value in metrics.items():
      metrics[metric]['average'] = torch.mean(torch.tensor(list(value.values()))).item()
    
    return metrics

def display_metrics(metrics, parent=None):
  console = Console()
  orig_parent = parent
  tree = parent if parent is not None else Tree(f"[magenta]current metrics[/magenta]")

  for key, value in metrics.items():
    # If it's a nested dictionary, we call display_metrics recursively
    if isinstance(value, dict):
      subtree = tree.add(f"[green]{key}[/green]")
      display_metrics(value, parent=subtree)
    elif isinstance(value, torch.Tensor):
      # Print tensor details
      formatted_tensor = format_tensor(value)
      tree.add(
        f"[cyan]{key}[/cyan]: {formatted_tensor}"
      )
    else:
      # Print non-tensor elements normally
      tree.add(f"[yellow]{key}[/yellow]: {value}")

  if orig_parent is None:
    console.print(tree)
  else:
    return tree
