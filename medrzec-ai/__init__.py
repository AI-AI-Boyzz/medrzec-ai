from enum import Enum, StrEnum, auto


class TextFormat(Enum):
    MARKDOWN = auto()
    SLACK = auto()


class FlowEnum(StrEnum):
    QUESTIONS_AND_PLAYBOOK = auto()
    REMOTE_WORK_SCORE = auto()
    AWESOME = auto()
