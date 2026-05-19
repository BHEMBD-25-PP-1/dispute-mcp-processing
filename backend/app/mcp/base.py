from abc import ABC, abstractmethod


class BaseMCPClient(ABC):

    @abstractmethod
    def call(self, service: str, payload: dict):
        pass