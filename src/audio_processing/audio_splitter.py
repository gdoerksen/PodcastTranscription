from abc import ABC, abstractmethod
from os import PathLike

class AudioSplitter(ABC):
    def __init__(self, 
                input_file: PathLike,
                output_directory: PathLike,
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
    def split(self)->list[PathLike] :
        ...