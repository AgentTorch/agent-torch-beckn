# substeps/order.py
# `order` confirmation

import torch
import torch.nn as nn
import random
from agent_torch.core.registry import Registry
from agent_torch.core.substep import (
    SubstepObservation,
    SubstepAction,
    SubstepTransition,
)
from ..utils import read_var


@Registry.register_substep("check_availability", "observation")
class CheckAvailability(SubstepObservation):
    def __init__(self, config, input_variables, output_variables, arguments):
        super().__init__(config, input_variables, output_variables, arguments)

    def forward(self, state):
        bpp_availability = read_var(state, self.input_variables["bpp_availability"])
        is_available = bpp_availability > 0

        return {"is_available": is_available}


@Registry.register_substep("confirm_order", "policy")
class ConfirmOrder(SubstepAction):
    def __init__(self, config, input_variables, output_variables, arguments):
        super().__init__(config, input_variables, output_variables, arguments)

    def forward(self, state, observation):
        is_available = observation["is_available"]

        # confirmation = torch.where(
        #     is_available,
        #     torch.ones_like(is_available, dtype=torch.int),
        #     torch.zeros_like(is_available, dtype=torch.int),
        # )
        rand_mat = torch.rand(is_available.shape)
        random_num = torch.randint(1, 3, (1,))[0]
        k_th_quant = torch.topk(rand_mat, is_available.shape[0] // random_num, dim=0, largest=False)[0][-1]
        confirmation = rand_mat <= k_th_quant

        return {"order_confirmation": confirmation}


@Registry.register_substep("update_order_status", "transition")
class UpdateOrderStatus(SubstepTransition):
    def __init__(self, config, input_variables, output_variables, arguments):
        super().__init__(config, input_variables, output_variables, arguments)

    def forward(self, state, action):
        bpp_availability = read_var(state, self.input_variables["bpp_availability"])
        bap_demand = read_var(state, self.input_variables["bap_demand"])
        order_bpp_id = read_var(state, self.input_variables["order_bpp_id"])
        order_bap_id = read_var(state, self.input_variables["order_bap_id"])
        order_status = read_var(state, self.input_variables["order_status"])
        confirmation = action["bpp"]["order_confirmation"]

        orders_to_update = order_status == 0
        selected_bpps = order_bpp_id[orders_to_update].int()
        involved_baps = order_bap_id[orders_to_update].int()
        confirmation_for_bpps = confirmation[selected_bpps] == 1

        i = 0
        for j, should_update in enumerate(orders_to_update):
            if not should_update:
                continue

            if confirmation_for_bpps[i] and bpp_availability[selected_bpps[i]] > bap_demand[involved_baps[i]]:
                order_status[j] = 1
                # bpp_availability[selected_bpps[i]] -= bap_demand[involved_baps[i]]
            else:
                order_status[j] = 4

            i += 1

        return {"order_status": order_status, "bpp_availability": bpp_availability}
