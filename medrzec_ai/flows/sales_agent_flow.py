from langchain import OpenAI
from medrzec_ai.agents.sales.agent import Agent, StageAnalyzerChain
from medrzec_ai.agents.sales.agent import ConversationChain
from medrzec_ai.database import Answer, Database, User
from .flow import Flow, FlowResponse


class SalesAgentChat(Flow):
    def __init__(self, db: Database, user: User) -> None:
        self.db = db
        self.lastQuestion = None
        llm = OpenAI()
        self.user = user
        self.agent = Agent(
            stage_analyzer_chain=StageAnalyzerChain.from_llm(llm),
            conversation_chain=ConversationChain.from_llm(llm),  # type: ignore
        )

    async def start_conversation(self) -> FlowResponse[str]:
        response = self.agent.step("hello")
        return FlowResponse(response)

    async def submit_message(self, message: str) -> FlowResponse[list[str]]:
        response = self.agent.step(message)

        if self.lastQuestion is not None:
            self.db.add_answer(
                answer=Answer(
                    question=self.lastQuestion, response=message, user_id=self.user.id
                ),
            )

        self.lastQuestion = response
        return FlowResponse([response])
