# main.py

from agent_torch.core import load_from_template

simulation = load_from_template(
  name = "beckn-solar",
  model = "./model",
  data = "./data",
  agents = {"bap": 8961, "bpp": 3840, "bg": 3},
  objects = {"order": 99999},
  substeps = {
    "0": "./model/substeps/search",
    "1": "./model/substeps/order",
    "2": "./model/substeps/fulfill",
    "3": "./model/substeps/pay",
    "4": "./model/substeps/apply"
  }
)

simulation.execute()

simulation.visualize("agents/bap/position", "agents/bap/grid_bill")
simulation.visualize("agents/bap/position", "agents/bap/solar_bill")
simulation.visualize("agents/bg/position", "agents/bg/wheeling_charges")
