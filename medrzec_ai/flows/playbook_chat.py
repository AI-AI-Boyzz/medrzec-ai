import os

import pinecone
from langchain.agents import AgentType, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.schema.output_parser import OutputParserException
from langchain.tools import Tool
from langchain.vectorstores import Pinecone

from .flow import Flow, FlowResponse


class PlaybookChat(Flow):
    def __init__(self, user_score: int) -> None:
        self.user_score = user_score

        pinecone.init(
            os.environ["PINECONE_API_KEY"], environment=os.environ["PINECONE_ENV"]
        )
        self.docsearch = Pinecone.from_existing_index(
            "playbook", OpenAIEmbeddings(client=None)
        )

        async def query_playbook(query: str) -> str:
            return "\n".join(self.get_relevant_fragments(query))

        tools = [
            Tool(
                "query_playbook",
                str,  # dummy sync function
                "Searches the People Managers guide for the query.",
                coroutine=query_playbook,
            )
        ]

        memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )

        self.agent = initialize_agent(
            tools,
            ChatOpenAI(temperature=0.9, model="gpt-4", client=None),
            AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            memory=memory,
        )

    async def start_conversation(self) -> FlowResponse[str]:
        for _ in range(5):
            try:
                response = await self.agent.arun(
                    input=f"""As an AI-powered chatbot, your goal is to help people managers become better at leading distributed teams. Your task is to help the user generate a bespoke plan for each company or team, pinpointing the areas that need improvement to optimize the remote work model. The plan can include recommendations on communication channels, collaboration, employee engagement, and more, based on chatbot vast dataset and understanding of effective remote work practices.

You should be able to help the user by querying the playbook content and answering their questions or requests for help based on the playbook content or best practices from the world's top remote companies, such as GitLab, Doist, Buffer, or Automattic.

It generates a bespoke plan for each company or team, pinpointing the areas that need enhancement to optimize the remote work model. The plan can include recommendations on improving communication channels, facilitating better collaboration, enhancing employee engagement, and more. These suggestions are based on chatbot vast dataset and understanding of effective remote work practices

The user has responded to questions regarding their remote work.
Their score was calculated to {self.user_score}%.

Remote work readiness scale:
Low: 0-50%
Medium: 51-90%
High: 91-100%

End your response by asking the user: "Which challenge do you want me to help you solve first?

Please add information about: 1. Problem description (eg. As a Director of Marketing, I have too many meetings. 2. Timezones differences (eg. Max 4h time difference). 3 Tools you are using (eg. Slack for sync, Notion for async). 4. Additional context (eg. We want to get an action plan how to become more asynchronous friendly in 30 days)." Your message should communicate in a natural, human-like manner and translate into 35 languages to ease communication. Always present the output in a reader-friendly, markdown-formatted style. Use emojis to highlight titles or subtitles for a fun and engaging read.

Please provide relevant and creative recommendations that are actionable and helpful to the user's specific needs and challenges. Encourage flexible and creative advice that addresses unique concerns while still maintaining a focus on accuracy and effectiveness.

Format your responses with Markdown and add emojis. During the conversation, always ask follow-up questions to the user to keep the conversation going."""
                )
            except OutputParserException as e:
                print(e)
            else:
                break
        else:  # output parsing failed 5 times in a row
            response = "Failed to generate a reply, sorry."

        return FlowResponse(response)

    async def submit_message(self, text: str) -> FlowResponse[list[str]]:
        response = await self.agent.arun(input=text)
        return FlowResponse([response])

    def get_relevant_fragments(self, query: str) -> list[str]:
        docs = self.docsearch.similarity_search(query)
        return [doc.page_content for doc in docs]
