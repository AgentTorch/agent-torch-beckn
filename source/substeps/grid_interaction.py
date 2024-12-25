import torch

from agent_torch.core.registry import Registry
from agent_torch.core.substep import (
    SubstepObservation,
    SubstepAction,
    SubstepTransition,
)

from utilities import *

# Grid Interaction
@Registry.register_substep("monitor_grid_status", "observation")
class MonitorGridStatus(SubstepObservation):
    def forward(self, state):
        current_load = read_var(state, self.input_variables['current_load'])
        max_capacity = read_var(state, self.input_variables['max_capacity'])
        reliability = read_var(state, self.input_variables['reliability'])
        power_balance = read_var(state, self.input_variables['power_balance'])
        
        # Calculate load ratio
        load_ratio = current_load / max_capacity
        
        # Calculate grid stability metric
        stability = reliability * (1.0 - torch.clamp(load_ratio, 0, 1))
        
        # Calculate available capacity
        available_capacity = torch.clamp(max_capacity - current_load, min=0)
        
        return {
            'grid_stability': stability,
            'available_capacity': available_capacity,
        }

@Registry.register_substep("adjust_grid_supply", "policy")
class AdjustGridSupply(SubstepAction):
    def forward(self, state, observation):
        current_price = read_var(state, self.input_variables['dynamic_price'])
        base_grid_price = read_var(state, self.input_variables['grid_price'])
        
        stability = observation['grid_stability']
        available_capacity = observation['available_capacity']
        
        # Dynamic pricing based on grid stability
        price_multiplier = torch.where(
            stability < 0.3,
            2.0,  # High stress: double price
            torch.where(
                stability < 0.7,
                1.5,  # Medium stress: 50% markup
                1.0   # Low stress: normal price
            )
        )
        
        updated_price = base_grid_price * price_multiplier
        
        # Calculate grid supply based on available capacity
        grid_supply = torch.where(
            stability > 0.2,
            available_capacity,
            available_capacity * stability * 5  # Reduce supply under stress
        )
        
        return {
            'grid_supply': grid_supply,
            'updated_price': updated_price
        }

@Registry.register_substep("update_grid_state", "transition")
class UpdateGridState(SubstepTransition):
    def forward(self, state, action):
        return {
            'current_load': action['grid_station']['grid_supply'],
            'dynamic_price': action['grid_station']['updated_price']
        }
