from __future__ import annotations

from enum import Enum, StrEnum, auto

from pydantic import BaseModel


class TextFormat(Enum):
    MARKDOWN = auto()
    SLACK = auto()


class FlowEnum(StrEnum):
    QUESTIONS_AND_PLAYBOOK = auto()
    REMOTE_WORK_SCORE_INTRO = auto()
    REMOTE_WORK_SCORE_TEAM_MEMBER = auto()
    REMOTE_WORK_SCORE_PEOPLE_LEADER = auto()
    AWESOME = auto()

    def as_suggestion(self) -> FlowSuggestion:
        match self:
            case FlowEnum.QUESTIONS_AND_PLAYBOOK:
                text = "Find out and help improve my Remote Work Score (legacy)"
            case FlowEnum.REMOTE_WORK_SCORE_INTRO:
                text = "Find out my Remote Work Score"
            case FlowEnum.REMOTE_WORK_SCORE_TEAM_MEMBER:
                text = "I'm a regular team member!"
            case FlowEnum.REMOTE_WORK_SCORE_PEOPLE_LEADER:
                text = "I'm a team leader!"
            case FlowEnum.AWESOME:
                text = "Tell me how awesome I am"

        return FlowSuggestion(id=self, text=text)


class FlowSuggestion(BaseModel):
    id: str
    text: str
