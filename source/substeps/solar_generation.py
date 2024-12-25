import torch

from agent_torch.core.registry import Registry
from agent_torch.core.substep import (
    SubstepObservation,
    SubstepAction,
    SubstepTransition,
)

from utilities import *

# Solar Generation and Battery Management
@Registry.register_substep("calculate_generation", "observation")
class CalculateSolarGeneration(SubstepObservation):
    def forward(self, state):
        has_solar = read_var(state, self.input_variables['has_solar'])
        generation_capacity = read_var(state, self.input_variables['generation_capacity'])

        current_month = int(state['environment']['current_month'].item() % 12)
        current_generation = generation_capacity[:, current_month]
        
        # Vectorized calculation of solar generation
        generated_power = has_solar.squeeze() * current_generation

        return {
            'generated_power': generated_power
        }

@Registry.register_substep("update_battery_storage", "policy")
class UpdateBatteryStorage(SubstepAction):
    def forward(self, state, observation):
        battery_capacity = read_var(state, self.input_variables['battery_capacity'])
        current_charge = read_var(state, self.input_variables['battery_charge'])
        demand = read_var(state, self.input_variables['demand_profile'])
        generated_power = observation['generated_power']
        
        # Calculate energy balance
        current_month = int(state['environment']['current_month'].item() % 12)
        current_demand = demand[:, current_month]

        # Energy surplus/deficit
        energy_balance = generated_power - current_demand
        
        # Battery efficiency
        charging_efficiency = 0.95
        discharging_efficiency = 0.95
        
        # Update battery charge
        new_charge =  current_charge.squeeze() + torch.where(
          energy_balance > 0,
          energy_balance * charging_efficiency,
          energy_balance / discharging_efficiency
        )
        # Clamp it to within the maximum capacity
        new_charge = torch.max(
          torch.min(new_charge, battery_capacity.squeeze()),
          torch.zeros_like(new_charge)
        )
        
        # Calculate excess energy after battery operations
        excess = torch.where(
            energy_balance > 0,
            torch.max(
              (energy_balance - (battery_capacity.squeeze() - current_charge.squeeze()) / charging_efficiency),
              torch.zeros_like(energy_balance)
            ),
            torch.zeros_like(energy_balance)
        )
        
        return {
            'battery_charge': new_charge.unsqueeze(1),
            'excess_energy': excess.unsqueeze(1)
        }

@Registry.register_substep("update_household_state", "transition")
class UpdateHouseholdState(SubstepTransition):
    def forward(self, state, action):
        state['environment']['current_month'] += 1

        return {
            'battery_charge': action['household']['battery_charge'],
            'excess_energy': action['household']['excess_energy']
        }
