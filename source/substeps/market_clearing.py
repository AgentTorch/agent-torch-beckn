import torch

from agent_torch.core.registry import Registry
from agent_torch.core.substep import (
    SubstepObservation,
    SubstepAction,
    SubstepTransition,
)

from utilities import *

@Registry.register_substep("aggregate_energy", "observation")
class AggregateEnergy(SubstepObservation):
    def forward(self, state):
        excess_energy = read_var(state, self.input_variables['excess_energy'])
        demand_profile = read_var(state, self.input_variables['demand_profile'])
        household_ids = read_var(state, self.input_variables['household_ids'])
        grid_station_id = read_var(state, self.input_variables['grid_station_id'])
        grid_prices = read_var(state, self.input_variables['dynamic_price'])
        
        current_month = int(state['environment']['current_month'].item() % 12)

        total_supply = torch.zeros_like(excess_energy)
        total_demand = torch.zeros_like(excess_energy)
        community_grid_prices = grid_prices[grid_station_id - 1]

        for i in range(len(household_ids)):
            idx = household_ids[i] - 1
            total_supply[idx] += excess_energy[idx]
            total_demand[idx] += demand_profile[idx, current_month].unsqueeze(1)

        return {
            'total_supply': total_supply,
            'total_demand': total_demand,
            'household_demand': demand_profile[:, current_month].unsqueeze(1),
            'community_grid_prices': community_grid_prices
        }

@Registry.register_substep("clear_market", "policy")
class ClearMarket(SubstepAction):
    def forward(self, state, observation):
        efficiency = read_var(state, self.input_variables['distribution_efficiency'])
        
        total_supply = observation['total_supply']
        total_demand = observation['total_demand']
        household_demand = observation['household_demand']
        grid_price = observation['community_grid_prices']
        
        base_price = 0.90 * grid_price
        
        supply_demand_ratio = torch.where(
            total_demand > 0,
            total_supply / total_demand,
            torch.ones_like(total_supply)
        )

        price_adjustment = torch.clamp(1.0 - supply_demand_ratio, -0.2, 0.2)
        market_price = base_price * (1.0 + price_adjustment)

        effective_supply = total_supply * efficiency.mean()
        power_balance = effective_supply - total_demand

        grid_needed = torch.clamp(-power_balance, min=0)
        demand_ratio = household_demand / (total_demand + 1e-8)
        household_grid_consumption = demand_ratio * grid_needed

        return {
            'market_price': market_price,
            'power_balance': power_balance,
            'grid_consumption': household_grid_consumption
        }

@Registry.register_substep("update_market_state", "transition")
class UpdateMarketState(SubstepTransition):
    def forward(self, state, action):
        return {
            'grid_consumption': action['community_coordinator']['grid_consumption'],
            'market_price': action['community_coordinator']['market_price'],
            'power_balance': action['community_coordinator']['power_balance'],
        }
