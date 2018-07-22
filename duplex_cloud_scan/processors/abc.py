from abc import ABC, abstractmethod
from datetime import datetime


class Processor(ABC):
    @abstractmethod
    def process(self, abs_filepath: str, file, dt: datetime):
        pass
