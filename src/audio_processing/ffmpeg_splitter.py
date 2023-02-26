import math 

from os import PathLike
from dataclasses import dataclass
from subprocess import run

from utils import LoggingObject

from .audio_splitter import AudioSplitter

MAX_DURATION_BEFORE_SPLIT_s = 3600 #TODO should be injected from config

@dataclass
class AudioSplit:
  order : int
  start_time_s : int
  end_time_s : int
  duration_s : int = 0
  file_name : str = ''

  def __post_init__(self):
    self.duration_s = self.end_time_s - self.start_time_s
    self.file_name = f"segment_{self.order:03d}.wav"

class FFmpegSplitter(LoggingObject, AudioSplitter):
    def __init__(
        self,
        name: str,
        input_file: PathLike,
        output_directory: PathLike,
        duration_s: float, #TODO could be derived from input_file
        split_s: int,
        overlap_s: int):
        
        super().__init__(
            name,
            input_file,
            output_directory,
            duration_s,
            split_s,
            overlap_s)

        """ audio splitter 
        input_file: PathLike 
        output_directory: PathLike

        duration_s: float
        split_s: float? 3600, subsegments are split into this size (plus the overlap)
        overlap_s: float? 300, overlap between subsegments
        """


    def split(self)->list[PathLike]:
        split_list = self._get_splits(self.duration_s)

        files_list = []
        # _split
        for split in split_list:
            output_file = self.output_directory / split.file_name
            command_line = f"ffmpeg -i {self.input_file} -ss {split.start_time_s} -to {split.end_time_s} -c copy {output_file}\n"
            command = command_line.split()
            output = run(command, capture_output=True )
            self.logger.debug(output)
            files_list.append(output_file)

        return files_list
        # end _split

    def _get_splits(self, duration_s: float)->list[AudioSplit]:
        audio_splits_list = []

        if duration_s > MAX_DURATION_BEFORE_SPLIT_s:
            number_of_splits = math.ceil(duration_s / self.split_s)
            for i in range(number_of_splits):
                if i==0:
                    start_time_s = i*self.split_s
                else:
                    start_time_s = i*self.split_s - self.overlap_s

                if i == (number_of_splits-1):
                # TODO using math.ceil here might cause DNE problems 
                    end_time_s = math.ceil( duration_s )
                else:
                    end_time_s = (i+1)*self.split_s

                order = i
                audiosplit = AudioSplit(order=order,
                                        start_time_s=start_time_s,
                                        end_time_s=end_time_s)
                audio_splits_list.append(audiosplit)
            
        else:
            audiosplit = AudioSplit(order=0,
                        start_time_s=0,
                        end_time_s=duration_s)
            audio_splits_list.append(audiosplit)

        return audio_splits_list

    def _split(self):
        pass
