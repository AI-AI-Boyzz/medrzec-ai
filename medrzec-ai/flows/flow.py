from __future__ import annotations

import dataclasses
from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from .. import FlowSuggestion

T = TypeVar("T")


class Flow(ABC):
    @abstractmethod
    async def start_conversation(self) -> FlowResponse[str]:
        ...

    @abstractmethod
    async def submit_message(self, text: str) -> FlowResponse[list[str]]:
        ...


@dataclasses.dataclass
class FlowResponse(Generic[T]):
    response: T
    flow_suggestions: list[FlowSuggestion] | None = None
    extra: dict[str, Any] = dataclasses.field(default_factory=dict)
