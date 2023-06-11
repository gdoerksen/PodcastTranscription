from abc import ABC, abstractmethod
from pathlib import Path

class AudioSplitter(ABC):
    def __init__(self, 
                input_file: Path,
                output_directory: Path,
                duration_s: float,
                split_s: int,
                overlap_s: int,
                ):
    
        self.input_file = input_file
        self.output_directory = output_directory
        self.duration_s = duration_s
        self.split_s = split_s
        self.overlap_s = overlap_s

    @abstractmethod
    def split(self)->list[Path] :
        ...