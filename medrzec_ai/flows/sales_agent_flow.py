from langchain import LLMChain, OpenAI
from medrzec_ai.agents.sales.agent import Agent, StageAnalyzerChain
from medrzec_ai.agents.sales.agent import ConversationChain
from medrzec_ai.agents.sales.data import CONVERSATION_STAGES
from medrzec_ai.apis.sentiment import analyze_sentiment
from medrzec_ai.database import Answer, Database, User
from .flow import Flow, FlowResponse


class SalesAgentChat(Flow):
    def __init__(self, db: Database, user: User | None) -> None:
        self.db = db
        self.lastQuestion = None
        self.interviewDone = False
        llm = OpenAI(model_name="gpt-4", temperature=0.5)
        self.user = user
        self.agent = Agent(
            stage_analyzer_chain=StageAnalyzerChain.from_llm(llm),
            conversation_chain=ConversationChain.from_llm(llm),  # type: ignore
        )

    async def start_conversation(self) -> FlowResponse[str]:
        response = self.agent.step("hello")
        return FlowResponse(response)

    async def submit_message(self, message: str) -> FlowResponse[list[str]]:
        if self.interviewDone:
            return FlowResponse(
                [
                    "The interview has already been completed. Buy our product to get more results!"
                ]
            )

        current_stage = CONVERSATION_STAGES[self.agent.current_stage]

        if current_stage.title == "Done":
            self.interviewDone = True
            score = self.db.get_score(self.user)
            message = await OpenAI(model_name="gpt-4", temperature=0.5).apredict(
                f"""
you were interviewing a user on his remote work performance and you got his remote work score wich is {score}/100 
Encourage the user to donate to the Remote-First Institute if they want to get more in-depth results, and personalized recommendations. Make sure you ask a apealing question to get the user attention - leverage the context data you have.

Make sure that the text is using the markdown language to make it pretty and use emotes to decorate it.
"""
            )

            return FlowResponse([message])

        response = self.agent.step(message)

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
