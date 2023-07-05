import dataclasses
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from .. import FlowSuggestion

T = TypeVar("T")


@dataclasses.dataclass
class FlowResponse(Generic[T]):
    response: T
    flow_suggestions: list[FlowSuggestion] | None = None


class Flow(ABC):
    @abstractmethod
    async def start_conversation(self) -> FlowResponse[str]:
        ...

    @abstractmethod
    async def submit_message(self, text: str) -> FlowResponse[list[str]]:
        ...
