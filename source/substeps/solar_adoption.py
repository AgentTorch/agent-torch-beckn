import torch

from agent_torch.core.registry import Registry
from agent_torch.core.substep import (
    SubstepObservation,
    SubstepAction,
    SubstepTransition,
)

from utilities import *

def read_var(state, var):
    return get_by_path(state, re.split("/", var))

# Solar Adoption Dynamics
@Registry.register_substep("evaluate_solar_potential", "observation")
class EvaluateSolarPotential(SubstepObservation):
    def forward(self, state):
        financial_capacity = read_var(state, self.input_variables['financial_capacity'])
        demand_profile = read_var(state, self.input_variables['demand_profile'])
        grid_consumption = read_var(state, self.input_variables['grid_consumption'])
        neighbor_adoption = read_var(state, self.input_variables['neighbor_adoption'])
        installation_cost = read_var(state, self.input_variables['installation_cost'])
        maintenance_cost = read_var(state, self.input_variables['maintenance_cost'])
        
        # Calculate neighbor influence
        social_influence = torch.mean(neighbor_adoption.float(), dim=1)
        
        # Calculate potential savings
        daily_consumption = torch.sum(demand_profile, dim=1)
        annual_consumption = daily_consumption * 365
        potential_savings = grid_consumption * state['environment']['grid_price'].item()
        
        # Calculate financial feasibility
        investment_ratio = installation_cost / financial_capacity
        maintenance_ratio = maintenance_cost / financial_capacity

        # Pack metrics into a tensor
        metrics = torch.stack([
            social_influence,
            potential_savings.squeeze(),
            investment_ratio.squeeze(),
            maintenance_ratio.squeeze()
        ], dim=1)
        
        return {
            'adoption_metrics': metrics
        }

@Registry.register_substep("make_adoption_decision", "policy")
class MakeAdoptionDecision(SubstepAction):
    def forward(self, state, observation):
        propensity = read_var(state, self.input_variables['adoption_propensity'])
        expected_roi = read_var(state, self.input_variables['expected_roi'])
        has_solar = read_var(state, self.input_variables['has_solar'])
        
        metrics = observation['adoption_metrics']
        social_influence = metrics[:, 0]
        potential_savings = metrics[:, 1]
        investment_ratio = metrics[:, 2]
        maintenance_ratio = metrics[:, 3]
        
        # Calculate adoption probability
        base_probability = propensity.squeeze() * social_influence
        
        # Adjust for financial factors
        financial_factor = torch.exp(-investment_ratio - maintenance_ratio)
        # roi_factor = torch.sigmoid(expected_roi.squeeze() - 0.15)  # 15% ROI threshold
        
        adoption_probability = base_probability * financial_factor # * roi_factor

        # Make decision (probabilistic)
        random_threshold = torch.rand_like(adoption_probability)
        adoption_decision = torch.logical_and(
            adoption_probability > random_threshold,
            torch.logical_not(has_solar.squeeze())  # Only adopt if don't already have solar
        )

        return {
            'adoption_decision': adoption_decision
        }

@Registry.register_substep("update_adoption_state", "transition")
class UpdateAdoptionState(SubstepTransition):
    def forward(self, state, action):
        has_solar = read_var(state, 'agents/household/has_solar')
        financial_capacity = read_var(state, 'agents/household/financial_capacity')
    
        adoption_decision = action['household']['adoption_decision']

        # Update financial capacity (subtract installation cost for new adopters)
        installation_cost = state['environment']['installation_cost'].item()
        financial_impact = torch.where(adoption_decision, -installation_cost, 0.0)
        
        return {
            'has_solar': torch.logical_or(has_solar.squeeze(), adoption_decision).unsqueeze(1),
            'financial_capacity': (financial_capacity.squeeze() + financial_impact).unsqueeze(1)
        }
