import os
from dataclasses import dataclass

@dataclass
class Config():
    FOLDER: os.PathLike
    DUMP_FILE: str


CONFIG = Config(
    FOLDER=os.path.join(os.getcwd(), 'data'),
    DUMP_FILE='dump.pickle'
)
