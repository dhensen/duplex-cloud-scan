from abc import ABC


class Processor(ABC):
    @abstractmethod
    def process(self, filepath):
        pass
