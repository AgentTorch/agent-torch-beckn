# substeps/pay.py
# `pay` operation

import torch
import torch.nn as nn
from agent_torch.core.registry import Registry
from agent_torch.core.substep import (
    SubstepObservation,
    SubstepAction,
    SubstepTransition,
)
from ..utils import read_var


@Registry.register_substep("get_order_details", "observation")
class GetOrderDetails(SubstepObservation):
    def __init__(self, config, input_variables, output_variables, arguments):
        super().__init__(config, input_variables, output_variables, arguments)

    def forward(self, state):
        order_bap_id = read_var(state, self.input_variables["order_bap_id"])
        order_bpp_id = read_var(state, self.input_variables["order_bpp_id"])
        order_bg_id = read_var(state, self.input_variables["order_bg_id"])
        order_status = read_var(state, self.input_variables["order_status"])

        solar_update_mask = order_status == 3
        solar_involved_baps = order_bap_id[solar_update_mask].int()
        solar_involved_bpps = order_bpp_id[solar_update_mask].int()
        solar_involved_bgs = order_bg_id[solar_update_mask].int()

        grid_update_mask = torch.logical_or(order_status == 3, order_status == 4)
        grid_involved_baps = order_bap_id[grid_update_mask].int()
        grid_involved_bpps = order_bpp_id[grid_update_mask].int()
        grid_involved_bgs = order_bg_id[grid_update_mask].int()

        return {
            "solar_details": {
                "involved_baps": solar_involved_baps,
                "involved_bpps": solar_involved_bpps,
                "involved_bgs": solar_involved_bgs,
                "orders_to_update": solar_update_mask,
            },
            "grid_details": {
                "involved_baps": grid_involved_baps,
                "involved_bpps": grid_involved_bpps,
                "involved_bgs": grid_involved_bgs,
                "orders_to_update": grid_update_mask,
            }
        }


@Registry.register_substep("calculate_payment", "policy")
class CalculatePayment(SubstepAction):
    def __init__(self, config, input_variables, output_variables, arguments):
        super().__init__(config, input_variables, output_variables, arguments)

    def forward(self, state, observation):
        bpp_price = read_var(state, self.input_variables["bpp_price"])
        bg_charge = read_var(state, self.input_variables["bg_charge"])
        bg_price = read_var(state, self.input_variables["bg_price"])
        order_quantity = read_var(state, self.input_variables["order_quantity"])

        payments_to_make = {}
        for type in ["solar", "grid"]:
          involved_baps, involved_bpps, involved_bgs, update_mask = (
              observation[f"{type}_details"]["involved_baps"],
              observation[f"{type}_details"]["involved_bpps"],
              observation[f"{type}_details"]["involved_bgs"],
              observation[f"{type}_details"]["orders_to_update"],
          )

          quantity_ordered = order_quantity[update_mask]
          payments_to_make[type] = torch.zeros(involved_baps.shape)

          for i, (bpp_id, bg_id) in enumerate(zip(involved_bpps, involved_bgs)):
              if type == "solar":
                  payments_to_make[type][i] = (bpp_price[bpp_id] * quantity_ordered[i]) + bg_charge[bg_id]
              else:
                  payments_to_make[type][i] = (bg_price[bg_id] * quantity_ordered[i])

        return {
            "payments_to_make": payments_to_make,
            "solar_details": observation["solar_details"],
            "grid_details": observation["grid_details"],
        }


@Registry.register_substep("update_wallets", "transition")
class UpdateWallets(SubstepTransition):
    def __init__(self, config, input_variables, output_variables, arguments):
        super().__init__(config, input_variables, output_variables, arguments)

    def forward(self, state, action):
        bap_solar_bill = read_var(state, self.input_variables["bap_solar_bill"])
        bap_grid_bill = read_var(state, self.input_variables["bap_grid_bill"])
        bpp_revenue = read_var(state, self.input_variables["bpp_revenue"])

        solar_involved_baps, solar_involved_bpps, solar_payments = (
            action["bap"]["solar_details"]["involved_baps"],
            action["bap"]["solar_details"]["involved_bpps"],
            action["bap"]["payments_to_make"]["solar"],
        )
        for i, bap_id in enumerate(solar_involved_baps):
            bap_solar_bill[bap_id] += solar_payments[i]
        for i, bpp_id in enumerate(solar_involved_bpps):
            bpp_revenue[bpp_id] += solar_payments[i]

        grid_involved_baps, grid_involved_bgs, grid_payments = (
            action["bap"]["grid_details"]["involved_baps"],
            action["bap"]["grid_details"]["involved_bgs"],
            action["bap"]["payments_to_make"]["grid"],
        )
        for i, bap_id in enumerate(grid_involved_baps):
            bap_grid_bill[bap_id] += grid_payments[i]

        print(bap_solar_bill, bap_grid_bill)
        return {"bap_solar_bill": bap_solar_bill, "bap_grid_bill": bap_grid_bill, "bpp_revenue": bpp_revenue}
