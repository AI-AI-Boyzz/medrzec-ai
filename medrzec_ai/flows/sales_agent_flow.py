from langchain import OpenAI

from medrzec_ai.agents.sales.agent import Agent, ConversationChain, StageAnalyzerChain
from medrzec_ai.agents.sales.data import CONVERSATION_STAGES, PAID_CONVERSATION_STAGES
from medrzec_ai.database import Database, User

from .flow import Flow, FlowResponse


class SalesAgentChat(Flow):
    def __init__(self, db: Database, user: User | None, user_token: str) -> None:
        self.conversation_stages = CONVERSATION_STAGES
        self.db = db
        self.lastQuestion = None
        llm = OpenAI(model_name="gpt-4", temperature=0.5)
        self.user = user
        self.user_token = user_token
        self.agent = Agent(
            stage_analyzer_chain=StageAnalyzerChain.from_llm(llm),
            conversation_chain=ConversationChain.from_llm(llm),  # type: ignore
        )

    async def start_conversation(self) -> FlowResponse[str]:
        response = self.agent.step("hello")
        return FlowResponse(response)

    async def submit_message(self, message: str) -> FlowResponse[list[str]]:
        if self.user and self.db.get_purchases(self.user.id):
            self.conversation_stages = (
                CONVERSATION_STAGES[:-1] + PAID_CONVERSATION_STAGES
            )

        response = self.agent.step(message)
        messages = [response]
        # current_stage = self.conversation_stages[self.agent.current_stage]

        # if self.lastQuestion is not None and self.user is not None:
        #     (score, magnitude) = analyze_sentiment(message)
        #     self.db.add_answer(
        #         answer=Answer(
        #             question=self.lastQuestion,
        #             response=message,
        #             user_id=self.user.id,
        #             topic=current_stage.topic,
        #             score=score,
        #             magnitude=magnitude,
        #         ),
        #     )

        if CONVERSATION_STAGES[self.agent.current_stage].title == "Done":
            url = f"https://ai-mentor-api.remote-first.institute/checkout-session?user_token={self.user_token}"
            messages.append(
                "Wanna unlock more insights and personalized recommendations? "
                f"Get access to **Distributed Work Pro Insights** — [donate now]({url})."
            )

        self.lastQuestion = response
        return FlowResponse(messages)
