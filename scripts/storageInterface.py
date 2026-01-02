from abc import ABC, abstractmethod

class DataStorage(ABC):
    @abstractmethod
    def save_header(self):
        pass
    
    @abstractmethod
    def save_item(self, data: dict):
        pass