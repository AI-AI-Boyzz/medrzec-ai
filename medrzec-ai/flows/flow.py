from abc import ABC, abstractmethod


class Flow(ABC):
    def __init__(self) -> None:
        self.flow_end = False

    @abstractmethod
    async def start_conversation(self) -> str:
        ...

    @abstractmethod
    async def submit_message(self, text: str) -> list[str]:
        ...
