# substeps/apply.py
# `apply` operation

import torch
import torch.nn as nn
from agent_torch.core.registry import Registry
from agent_torch.core.substep import (
    SubstepObservation,
    SubstepAction,
    SubstepTransition,
)
from ..utils import read_var

@Registry.register_substep("calculate_availability", "policy")
class CalculateAvailability(SubstepAction):
    def __init__(self, config, input_variables, output_variables, arguments):
        super().__init__(config, input_variables, output_variables, arguments)
        self.time = 1;
        self.ratios = [1, 0.9, 0.9, 0.7, 0.5, 0.6]

    def forward(self, state, observation):
        bpp_availability = read_var(state, self.input_variables["bpp_availability"])
        bpp_max_capacity = read_var(state, self.input_variables["bpp_max_capacity"])

        bpp_availability = bpp_max_capacity * self.ratios[self.time]
        return {"bpp_availability": bpp_availability}


@Registry.register_substep("update_bpp_availability", "transition")
class UpdateBPPAvailability(SubstepTransition):
    def __init__(self, config, input_variables, output_variables, arguments):
        super().__init__(config, input_variables, output_variables, arguments)

    def forward(self, state, action):
        return {"bpp_availability": action["bpp"]["bpp_availability"]}
