# substeps/restock.py
# `restock` operation

import torch
import torch.nn as nn
from agent_torch.core.registry import Registry
from agent_torch.core.substep import (
    SubstepObservation,
    SubstepAction,
    SubstepTransition,
)
from .utils import read_var


@Registry.register_substep("calculate_salary", "policy")
class CalculateSalary(SubstepAction):
    def __init__(self, config, input_variables, output_variables, arguments):
        super().__init__(config, input_variables, output_variables, arguments)

    def forward(self, state, observation):
        bap_wallet = read_var(state, self.input_variables["bap_wallet"])

        bap_wallet = torch.where(bap_wallet < 0, abs(bap_wallet) / 2, bap_wallet)
        
        return {"bap_wallet": bap_wallet}


@Registry.register_substep("calculate_availability", "policy")
class CalculateAvailability(SubstepAction):
    def __init__(self, config, input_variables, output_variables, arguments):
        super().__init__(config, input_variables, output_variables, arguments)

    def forward(self, state, observation):
        bpp_capacity = read_var(state, self.input_variables["bpp_capacity"])
        bpp_max_capacity = read_var(state, self.input_variables["bpp_max_capacity"])

        bpp_capacity += bpp_max_capacity / 3
        bpp_capacity = torch.where(bpp_capacity < 0, abs(bpp_capacity) / 2, bpp_capacity)
        bpp_capacity = torch.where(
            bpp_capacity > bpp_max_capacity, bpp_max_capacity, bpp_capacity
        )

        return {"bpp_capacity": bpp_capacity}


@Registry.register_substep("update_bpp_availability_and_bap_wallet", "transition")
class UpdateBPPAvailabilityAndBAPWallet(SubstepTransition):
    def __init__(self, config, input_variables, output_variables, arguments):
        super().__init__(config, input_variables, output_variables, arguments)

    def forward(self, state, action):
        return {"bap_wallet": action["bap"]["bap_wallet"], "bpp_capacity": action["bpp"]["bpp_capacity"]}
