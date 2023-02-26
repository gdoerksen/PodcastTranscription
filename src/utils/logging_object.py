from typing import Optional
import logging 

class LoggingObject:
    """
    A mixin class that implements a logging object.
    """

    def __init__(self, name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.logger = logging.getLogger(self.name)

    def __str__(self):
        return self.name