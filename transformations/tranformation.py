from abc import ABC, abstractmethod

class Transformation(ABC):
    @abstractmethod
    def is_applicable(self, code: str) -> bool:
        pass

    @abstractmethod
    def transform(self, code: str) -> str:
        pass