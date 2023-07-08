from langchain import OpenAI
from medrzec_ai.agents.sales.agent import Agent, StageAnalyzerChain, ConversationChain
# from medrzec_ai.database import Database
from .flow import Flow, FlowResponse


class SalesAgentChat(Flow):
    def __init__(self) -> None:
        llm = OpenAI(model_name="gpt-4", temperature=0.5)
        self.agent = Agent(
            stage_analyzer_chain=StageAnalyzerChain.from_llm(llm),
            conversation_chain=ConversationChain.from_llm(llm),
        )

    async def start_conversation(self) -> FlowResponse[str]:
        response = self.agent.step("hello")
        return FlowResponse(response)

    async def submit_message(self, message: str) -> FlowResponse[list[str]]:
        response = self.agent.step(message)
        # Database.add_answer(message)
        return FlowResponse([response])
