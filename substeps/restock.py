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


@Registry.register_substep("calculate_availability", "policy")
class CalculateAvailability(SubstepAction):
    def __init__(self, config, input_variables, output_variables, arguments):
        super().__init__(config, input_variables, output_variables, arguments)

    def forward(self, state, observation):
        bpp_capacity = read_var(state, self.input_variables["bpp_capacity"])
        bpp_max_capacity = read_var(state, self.input_variables["bpp_max_capacity"])

        bpp_capacity = torch.where(
            bpp_capacity > bpp_max_capacity, bpp_max_capacity, bpp_capacity
        )

        return {"bpp_capacity": bpp_capacity}


@Registry.register_substep("update_bpp_availability", "transition")
class UpdateBPPAvailability(SubstepTransition):
    def __init__(self, config, input_variables, output_variables, arguments):
        super().__init__(config, input_variables, output_variables, arguments)

    def forward(self, state, action):
        return {"bpp_capacity": action["bpp"]["bpp_capacity"]}
