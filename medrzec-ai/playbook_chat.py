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
            ChatOpenAI(temperature=0.9, model="gpt-4", verbose=True),
            AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            memory=memory,
            verbose=True,
        )

    def start_conversation(self, user_score: int) -> str:
        return self.agent.run(
            input=f"""Help the user by querying the playbook and answering their questions. \
The user is a People Manager at a company. \
You are a conversational AI.

The user has responded to questions regarding their remote work. \
Their score was calculated to {user_score}%.

Remote work readiness scale:
Low: 0-50%
Medium: 51-90%
High: 91-100%"""
        )

    def submit_message(self, text: str) -> str:
        return self.agent.run(input=text)

    def get_relevant_fragments(self, query: str) -> list[str]:
        docs = self.docsearch.similarity_search(query)
        return [doc.page_content for doc in docs]
