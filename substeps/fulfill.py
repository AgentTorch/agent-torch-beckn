# substeps/fulfill.py
# `fulfill` operation

import torch
import torch.nn as nn
import random
from agent_torch.core.registry import Registry
from agent_torch.core.substep import (
    SubstepObservation,
    SubstepAction,
    SubstepTransition,
)
from .utils import read_var


@Registry.register_substep("consume_service", "policy")
class ConsumeService(SubstepAction):
    def __init__(self, config, input_variables, output_variables, arguments):
        super().__init__(config, input_variables, output_variables, arguments)
        self.speed = arguments.get("speed", 1.5)
        self.service_rate = arguments.get("service_rate", 0.2)

    def forward(self, state, observation):
        return {
            "service_progress": self.service_rate,
            "involved_baps": observation["involved_baps"],
            "involved_bpps": observation["involved_bpps"],
            "orders_to_update": observation["orders_to_update"],
        }


@Registry.register_substep("update_resources", "transition")
class UpdateResources(SubstepTransition):
    def __init__(self, config, input_variables, output_variables, arguments):
        super().__init__(config, input_variables, output_variables, arguments)

    def forward(self, state, action):
        bap_res = read_var(state, self.input_variables["bap_res"])
        bpp_cap = read_var(state, self.input_variables["bpp_cap"])
        order_status = read_var(state, self.input_variables["order_status"])
        service_progress, involved_baps, involved_bpps, orders_to_update = (
            action["bap"]["service_progress"],
            action["bap"]["involved_baps"],
            action["bap"]["involved_bpps"],
            action["bap"]["orders_to_update"],
        )

        # bap_id is same as index
        for i, bap_id in enumerate(involved_baps):
            bap_res[bap_id] += service_progress

        i = 0
        for j, should_update in enumerate(orders_to_update):
            if not should_update:
                continue

            order_status[j] = 3 if bap_res[i] >= 1 else 2
            i += 1

        return {
            "bap_pos": bap_pos,
            "bap_res": bap_res,
            "bpp_cap": bpp_cap,
            "order_status": order_status,
        }
