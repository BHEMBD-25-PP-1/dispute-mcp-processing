from abc import ABC, abstractmethod


class BaseLLMClient(ABC):

    @abstractmethod
    def chat(self, prompt: str) -> str:
        pass