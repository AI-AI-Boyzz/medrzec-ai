import dataclasses
from abc import ABC, abstractmethod
from typing import Generic, Self, TypeVar

from pydantic import BaseModel

from .. import FlowEnum

T = TypeVar("T")


class FlowSuggestion(BaseModel):
    id: str
    text: str

    @classmethod
    def from_flow(cls, flow: FlowEnum) -> Self:
        match flow:
            case FlowEnum.QUESTIONS_AND_PLAYBOOK:
                text = "Find out and help improve my Remote Work Score"
            case FlowEnum.REMOTE_WORK_SCORE:
                text = "Find out my Leader Remote Work Score"
            case FlowEnum.AWESOME:
                text = "Tell me how awesome I am"

        return cls(id=flow, text=text)


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
