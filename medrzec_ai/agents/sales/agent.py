from __future__ import annotations
from dataclasses import dataclass, field
from langchain import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms import BaseLLM
from langchain.schema import BaseLLMOutputParser, Generation
import re

from .data import STAGE_ANALYZER_PROMPT, CONVERSATION_PROMPT
from .data import CONVERSATION_STAGES


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
                    "conversation_stages": "\n-------\n".join(
                        f"{i}: {stage.title}:\n{stage.prompt}"
                        for i, stage in enumerate(CONVERSATION_STAGES)
                    ),
                    "conversation_stage_id": self.current_stage or "(none)",
                }
            )["text"]
        )

        current_conversation_stage = CONVERSATION_STAGES[self.current_stage]

        ai_message = self.conversation_chain(
            {
                "current_conversation_stage": f"{current_conversation_stage.title}\n{current_conversation_stage.prompt}\n---",
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
        return cls(prompt=prompt, llm=llm, verbose=verbose, output_parser=StageAnalyzerOutputParser())


class ConversationChain(LLMChain):
    @classmethod
    def from_llm(cls, llm: BaseLLM, verbose: bool = True) -> LLMChain:
        prompt = PromptTemplate(
            template=CONVERSATION_PROMPT,
            input_variables=[
                "current_conversation_stage",
                "conversation_history",
            ],
        )
        return cls(prompt=prompt, llm=llm, verbose=verbose)


class StageAnalyzerOutputParser(BaseLLMOutputParser[int]):
    def parse_result(self, result: list[Generation]) -> int:
        index = int(re.search(r'\d+', result[0].text).group())
        return min(index, len(CONVERSATION_STAGES) - 1)
