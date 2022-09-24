import os
from dataclasses import dataclass

@dataclass
class Config():
    DATA_FOLDER: os.PathLike
    DUMP_FOLDER: os.PathLike
    DUMP_FILE: str


CONFIG = Config(
    DATA_FOLDER=os.path.join(os.getcwd(), 'data'),
    DUMP_FOLDER=os.path.join(os.getcwd(), 'dump'),
    DUMP_FILE=os.path.join(os.getcwd(), 'dump/' 'dump.pickle')
)
