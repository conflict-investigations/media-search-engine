import json

from dataclasses import asdict, dataclass
from urllib import request
from typing import List

from .base import DataSource

# https://www.scribblemaps.com/maps/view/Operational%20Map%20Ukraine/nBT8ffpeGH
# https://widgets.scribblemaps.com/api/maps/nBT8ffpeGH/smjsonLocal
# 3.5mb
