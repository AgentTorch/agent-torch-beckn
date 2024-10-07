# substeps/search.py
# `search` operation

import torch
import torch.nn as nn
from haversine import haversine_vector, Unit
from agent_torch.core.registry import Registry
from agent_torch.core.substep import (
    SubstepObservation,
    SubstepAction,
    SubstepTransition,
)
from ..utils import read_var


@Registry.register_substep("find_nearby_bpps_and_bgs", "observation")
class FindNearbyBPPsAndBGs(SubstepObservation):
    def __init__(self, config, input_variables, output_variables, arguments):
        super().__init__(config, input_variables, output_variables, arguments)
        self.computed_distances = None

    def forward(self, state):
        bap_positions = read_var(state, self.input_variables["bap_positions"])
        bpp_positions = read_var(state, self.input_variables["bpp_positions"])
        bg_positions = read_var(state, self.input_variables["bg_positions"])

        if self.computed_distances is None:
            self.computed_distances = {}
            self.computed_distances["bpp"] = torch.tensor(
              haversine_vector(
                bpp_positions.numpy(),
                bap_positions.numpy(),
                Unit.KILOMETERS, comb=True
              )
            )
            self.computed_distances["bg"] = torch.tensor(
              haversine_vector(
                bg_positions.numpy(),
                bap_positions.numpy(),
                Unit.KILOMETERS, comb=True
              )
            )

        return {"distances": self.computed_distances}


@Registry.register_substep("select_bpp", "policy")
class SelectBPPAndBG(SubstepAction):
    def __init__(self, config, input_variables, output_variables, arguments):
        super().__init__(config, input_variables, output_variables, arguments)
        self.price_weight = arguments.get("price_weight", 0.2)
        self.distance_weight = arguments.get("distance_weight", 0.4)
        self.stochasticity = arguments.get("stochasticity", 0.4)

    def forward(self, state, observation):
        bpp_prices = read_var(state, self.input_variables["bpp_prices"])
        bpp_availability = read_var(state, self.input_variables["bpp_availability"])
        bg_charges = read_var(state, self.input_variables["bg_charges"])
        search_radius = read_var(state, self.input_variables["search_radius"])

        bpp_distances, bg_distances = observation["distances"]["bpp"], observation["distances"]["bg"]
        bpp_mask = (bpp_distances <= search_radius) # & (bpp_availability > 0)

        # Normalize distances and prices
        max_bpp_distance = torch.max(bpp_distances)
        normalized_bpp_distances = bpp_distances / max_bpp_distance
        max_bg_distance = torch.max(bg_distances)
        normalized_bg_distances = bg_distances / max_bg_distance
        max_price = torch.max(bpp_prices)
        normalized_prices = bpp_prices / max_price
        max_charge = torch.max(bg_charges)
        normalized_charges = bg_charges / max_charge

        dimensionalize = (
            lambda x, y: torch.flatten(x.T)
            .unsqueeze(0)
            .repeat(y.shape[0], 1)
        )
        bpp_scores = (
            self.price_weight * dimensionalize(normalized_prices, normalized_bpp_distances)
            + self.distance_weight * normalized_bpp_distances
            + self.stochasticity * (1 - torch.rand((1))[0])
        )
        bg_scores = (
            self.price_weight * dimensionalize(normalized_charges, normalized_bg_distances)
            + self.distance_weight * normalized_bg_distances
        )

        # Set scores for entities that are too far to a large value
        bpp_scores[~bpp_mask] = float("inf")

        # Select the BPP with the lowest score for each BAP
        selected_bpp_indices = torch.argmin(bpp_scores, dim=1)
        selected_bpp_indices = selected_bpp_indices[selected_bpp_indices.nonzero()]
        selected_bg_indices = torch.argmin(bg_scores, dim=1)
        selected_bg_indices = selected_bg_indices[selected_bg_indices.nonzero()]

        return {"selected_bpps": selected_bpp_indices, "selected_bgs": selected_bg_indices}


@Registry.register_substep("create_order", "transition")
class CreateOrder(SubstepTransition):
    def __init__(self, config, input_variables, output_variables, arguments):
        super().__init__(config, input_variables, output_variables, arguments)

    def forward(self, state, action):
        selected_bpps = action["bap"]["selected_bpps"]
        selected_bgs = action["bap"]["selected_bgs"]
        bap_ids = read_var(state, self.input_variables["bap_id"])
        resource_demand = read_var(state, self.input_variables["resource_demand"])
        order_bap_id = read_var(state, self.input_variables["order_bap_id"])
        order_bpp_id = read_var(state, self.input_variables["order_bpp_id"])
        order_bg_id = read_var(state, self.input_variables["order_bg_id"])
        order_quantity = read_var(state, self.input_variables["order_quantity"])
        order_status = read_var(state, self.input_variables["order_status"])
        last_order_id = read_var(state, self.input_variables["last_order_id"])

        next_order_id = int((last_order_id + 1).item())
        for i, (bap_id, bpp_id, bg_id, quantity) in enumerate(
            zip(bap_ids, selected_bpps, selected_bgs, resource_demand)
        ):
            order_bap_id[next_order_id + i] = bap_id
            order_bpp_id[next_order_id + i] = bpp_id
            order_bg_id[next_order_id + i] = bg_id
            order_quantity[next_order_id + i] = quantity
            order_status[next_order_id + i] = 0

        return {
            "order_bap_id": order_bap_id,
            "order_bpp_id": order_bpp_id,
            "order_bg_id": order_bg_id,
            "order_quantity": order_quantity,
            "order_status": order_status,
        }
