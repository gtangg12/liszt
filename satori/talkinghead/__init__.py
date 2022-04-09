import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__)))

from tha2.util import *
from tha2.poser.modes.mode_20 import create_poser, get_pose_parameters

sys.path.pop()
