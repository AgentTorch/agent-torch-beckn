# ---------------------------------------------------------
# main.py
# ---------------------------------------------------------

from agent_torch.core import Registry, Runner
from agent_torch.core.helpers import read_from_file

from utilities import *
from substeps import *

CONFIG_FILE = 'config/solar.yaml'
parsed, config = parse_config(CONFIG_FILE)

registry = Registry()
registry.register(read_from_file, 'read_from_file', 'initialization')

runner = Runner(parsed, registry)
runner.init()

steps = config['simulation']['steps']
for step in range(steps):
  runner.step(1)

  current_state = runner.state_trajectory[-1][-1]

  inspect_tensor(f'state at step {step}', current_state)
  display_metrics(calculate_metrics(current_state))
