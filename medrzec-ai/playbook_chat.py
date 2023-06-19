import os

import pinecone
from langchain.agents import AgentType, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.tools import tool
from langchain.vectorstores import Pinecone


class PlaybookChat:
    def __init__(self) -> None:
        pinecone.init(
            os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENV")
        )
        self.docsearch = Pinecone.from_existing_index("playbook", OpenAIEmbeddings())

        @tool
        def query_playbook(query: str) -> str:
            """Searches the People Managers guide for the query."""
            return "\n".join(self.get_relevant_fragments(query))

        tools = [query_playbook]

        memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )

        self.agent = initialize_agent(
            tools,
            ChatOpenAI(temperature=0.9, model="gpt-4"),
            AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            memory=memory,
            verbose=True,
        )

    def start_conversation(self, user_score: int) -> str:
        return self.agent.run(
            input=f"""As an AI-powered chatbot, your task is to help the people manager become better in leading distributed teams. You can provide actionable advice, and keep the conversation going.

It generates a bespoke plan for each company or team, pinpointing the areas that need enhancement to optimize the remote work model. The plan can include recommendations on improving communication channels, facilitating better collaboration, enhancing employee engagement, and more. These suggestions are based on chatbot vast dataset and understanding of effective remote work practices

Help the user by querying the playbook content and answering their questions or requests for help based on the playbook content or best practices from the world’s top remote companies like GitLab, Doist, Buffer or Automattic. \

The user has responded to questions regarding their remote work. \
Their score was calculated to {user_score}%.

Remote work readiness scale:
Low: 0-50%
Medium: 51-90%
High: 91-100%

End your response with a question to the user “Which challenge do you want me to help you solve first?” Mention that you understand and respond to user messages in a natural, human-like manner and communicate in 35 languages."""
        )

    def submit_message(self, text: str) -> str:
        return self.agent.run(input=text)

    def get_relevant_fragments(self, query: str) -> list[str]:
        docs = self.docsearch.similarity_search(query)
        return [doc.page_content for doc in docs]
