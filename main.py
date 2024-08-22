# main.py
# runs the simulation

import argparse
from tqdm import trange

from agent_torch.core import Registry, Runner
from agent_torch.core.visualize import GeoPlot
from agent_torch.core.helpers import read_config, read_from_file
from substeps import *
from helpers import *

print(":: execution started")

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config", help="path to yaml config file")
config_file = parser.parse_args().config

config = read_config(config_file)
metadata = config.get("simulation_metadata")
num_episodes = metadata.get("num_episodes")
num_steps_per_episode = metadata.get("num_steps_per_episode")
visualize = metadata.get("visualize")

registry = Registry()
registry.register(read_from_file, "read_from_file", "initialization")

runner = Runner(config, registry)
runner.init()

print(":: preparing simulation...")

state_trajectories = []
for episode in trange(num_episodes, desc=f":: running episode", ncols=108):
    runner.reset()

    for _ in trange(num_steps_per_episode, desc=f":: running steps", ncols=72):
        runner.step(1)
    state_trajectories.append(runner.state_trajectory)

print(":: execution completed")

print(":: generating geoplot")

plot = GeoPlot(
  config, state_trajectories,
  "data/roofs.geojson",
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI2MzllOTJmMy01YmUzLTQwZDQtOGMyYy04NDdlODUyYjc1MzYiLCJpZCI6MjM1NDMxLCJpYXQiOjE3MjM5ODc4ODZ9.CxqymuvZilCWP8dv01j-4634W7PQhcI_DuT-gfRS3dc"
)
plot.visualize("agents/bap/position", "agents/bap/wallet")

print(":: geojson generated")
