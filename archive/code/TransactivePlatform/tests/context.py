import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import components.Carpooler as Carpooler
import components.Prosumer as Prosumer
#import components.Prosumer as Prosumer
# ^ not needed, because TrasactivePlatfrom was added to the the path, and components has __init__.py,
# but I'd rather be explicit about why access to Prosumer is possible
