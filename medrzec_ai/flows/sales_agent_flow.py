from langchain import OpenAI

from medrzec_ai.agents.sales.agent import Agent, ConversationChain, StageAnalyzerChain
from medrzec_ai.agents.sales.data import CONVERSATION_STAGES, PAID_CONVERSATION_STAGES
from medrzec_ai.apis.sentiment import analyze_sentiment
from medrzec_ai.database import Answer, Database, User

from .flow import Flow, FlowResponse


class SalesAgentChat(Flow):
    def __init__(self, db: Database, user: User | None) -> None:
        # TODO: Only add paid conversation stages if user is paid
        self.conversation_stages = CONVERSATION_STAGES + PAID_CONVERSATION_STAGES
        self.db = db
        self.lastQuestion = None
        llm = OpenAI(model_name="gpt-4", temperature=0.5)
        self.user = user
        self.agent = Agent(
            stage_analyzer_chain=StageAnalyzerChain.from_llm(
                llm, self.conversation_stages
            ),
            conversation_chain=ConversationChain.from_llm(llm),  # type: ignore
            conversation_stages=self.conversation_stages,
        )

    async def start_conversation(self) -> FlowResponse[str]:
        response = self.agent.step("hello")
        return FlowResponse(response)

    async def submit_message(self, message: str) -> FlowResponse[list[str]]:
        response = self.agent.step(message)
        current_stage = self.conversation_stages[self.agent.current_stage]

        if self.lastQuestion is not None and self.user is not None:
            (score, magnitude) = analyze_sentiment(message)
            self.db.add_answer(
                answer=Answer(
                    question=self.lastQuestion,
                    response=message,
                    user_id=self.user.id,
                    topic=current_stage.topic,
                    score=score,
                    magnitude=magnitude,
                ),
            )

        self.lastQuestion = response
        return FlowResponse([response])
