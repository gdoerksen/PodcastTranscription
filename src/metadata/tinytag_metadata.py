from dataclasses import dataclass
from os import PathLike
from tinytag import TinyTag

from utils import LoggingObject

from .metadata import AudioMetadata


class TinyTagAudioMetadata(LoggingObject, AudioMetadata):
        
    def __init__(self, name: str, path: PathLike):
        super().__init__(name, path)

        try: 
            tag = TinyTag.get(path)
        except FileNotFoundError as e:
            self.logger.exception(e)
            raise e
            
        self.duration_s = tag.duration
        self.sample_rate_hz = tag.samplerate
        self.bitrate_kbps = tag.bitrate
        self.album = tag.album
        self.artist = tag.artist
        self.title = tag.title
        self.composer = tag.composer