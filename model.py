# models/solar-network

import os 
dir_path = os.path.dirname(os.path.realpath(__file__))

from .substeps import *
from .helpers import *

def get_model_metadata():
  config_path = f"{dir_path}/config.yaml"

  return {"config_path": config_path}
