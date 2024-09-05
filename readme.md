# AgentTorch: Beckn Solar Energy Network Model

## Overview

AgentTorch is a differentiable learning framework that enables you to
run simulations with over millions of autonomous agents.
[Beckn](https://becknprotocol.io) is a protocol that enables the
creation of open, peer-to-peer decentralized networks for pan-sector
economic transactions.

This model integrates Beckn with AgentTorch, to simulate a solar energy
network in which households in a locality can decide to either buy solar
panels and act as providers of solar energy, or decide to use the energy
provided by other households instead of installing solar panels
themselves.

## Getting Started

You can run the simulation on your machine, with your own data, in just
a few lines of code:

```py
from agent_torch.core import create_from_template

# create a simulation from a template.
simulation = create_from_template(
  model = "./model",
  data = "./data",
  agents = {"bap": 8961, "bpp": 3840},
  objects = {"order": 99999},
)

# execute the simulation, and generate visualizations.
simulation.execute()
```

The `model` folder is this repository, and can be cloned via `git`, or
downloaded from
[this](https://github.com/AgentTorch/agent-torch-beckn/archive/refs/heads/beckn-solar.zip)
link.

The `data` folder must be structured as follows:

```
data/
├── bap
│  ├── position.csv
│  └── wallet.csv
└── bpp
   ├── available_capacity.csv
   ├── max_capacity.csv
   └── position.csv
```

## Model Specifications

The details regarding the model can be found in the
[model card](model_card.md).
