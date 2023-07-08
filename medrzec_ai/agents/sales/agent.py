from __future__ import annotations
from typing import Any
from dataclasses import dataclass, field
from langchain import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms import BaseLLM

from .data import STAGE_ANALYZER_PROMPT, CONVERSATION_PROMPT, CONVERSATION_STAGES


@dataclass
class Agent:
    stage_analyzer_chain: StageAnalyzerChain
    conversation_chain: ConversationChain
    conversation_history: list[str] = field(default_factory=list)
    current_stage: int = 0

    def step(self, user_message: str) -> str:
        self.conversation_history.append(f"User: {user_message}")

        self.current_stage = int(
            self.stage_analyzer_chain(
                {
                    "conversation_history": "\n".join(self.conversation_history),
                    "conversation_stages": "\n".join(
                        f"{i}: {stage.title}: {stage.prompt}"
                        for i, stage in enumerate(CONVERSATION_STAGES)
                    ),
                    "conversation_stage_id": self.current_stage,
                }
            )["text"]
        )
        current_conversation_stage = CONVERSATION_STAGES[self.current_stage]

        ai_message = self.conversation_chain(
            {
                "current_conversation_stage": f"{current_conversation_stage.title}: {current_conversation_stage.prompt}",
                "conversation_history": "\n".join(self.conversation_history),
            }
        )["text"]
        self.conversation_history.append(f"AI: {ai_message}")
        return ai_message


class StageAnalyzerChain(LLMChain):
    @classmethod
    def from_llm(cls, llm: BaseLLM, verbose: bool = True) -> LLMChain:
        prompt = PromptTemplate(
            template=STAGE_ANALYZER_PROMPT,
            input_variables=[
                "conversation_history",
                "conversation_stages",
                "conversation_stage_id",
            ],
        )
        return cls(prompt=prompt, llm=llm, verbose=verbose)


class ConversationChain(LLMChain):
    @classmethod
    def from_llm(cls, llm: BaseLLM, verbose: bool = True) -> LLMChain:
        prompt = PromptTemplate(
            template=CONVERSATION_PROMPT,
            input_variables=["current_conversation_stage", "conversation_history"],
        )
        return cls(prompt=prompt, llm=llm, verbose=verbose)
