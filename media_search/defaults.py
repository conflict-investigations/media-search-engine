import os
from dataclasses import dataclass

@dataclass
class Config():
    DATA_FOLDER: str
    DUMP_FOLDER: str
    DUMP_FILE: str
    CONFIG_FILE: str
    LOGGING: bool


CONFIG = Config(
    DATA_FOLDER=os.path.join(os.getcwd(), 'data'),
    DUMP_FOLDER=os.path.join(os.getcwd(), 'dump'),
    DUMP_FILE=os.path.join(os.getcwd(), 'dump/' 'dump.pickle'),
    CONFIG_FILE='config.json',
    LOGGING=False,
)
