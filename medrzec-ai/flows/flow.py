from abc import ABC, abstractmethod


class Flow(ABC):
    @abstractmethod
    def start_conversation(self) -> str:
        ...

    @abstractmethod
    def submit_message(self, text: str) -> list[str]:
        ...
