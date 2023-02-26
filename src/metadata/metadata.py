from os import PathLike
from dataclasses import dataclass
from abc import ABC

@dataclass
class AudioMetadata(ABC):
    path: PathLike
    duration_s : float
    sample_rate_hz : int
    bitrate_kbps : float
    album : str
    artist : str
    title : str
    composer : str
    
    def __init__(self, path: PathLike):
        self.path = path