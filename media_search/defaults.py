import os
from dataclasses import dataclass

@dataclass
class Config():
    DATA_FOLDER: str
    DUMP_FOLDER: str
    DUMP_FILE: str
    CONFIG_FILE: str
    LOGGING: bool
    MAX_CONTENT_LENGTH: int


CONFIG = Config(
    DATA_FOLDER=os.path.join(os.getcwd(), 'data'),
    DUMP_FOLDER=os.path.join(os.getcwd(), 'dump'),
    DUMP_FILE=os.path.join(os.getcwd(), 'dump/' 'dump.pickle'),
    CONFIG_FILE='config.json',
    LOGGING=False,
    MAX_CONTENT_LENGTH=1024 * 1024,  # File uploads limited to 1MB
)
