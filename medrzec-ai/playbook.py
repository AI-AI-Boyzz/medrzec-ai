import os

import pinecone
from langchain.agents import AgentType, initialize_agent, load_tools
from langchain.chains import ConversationalRetrievalChain, LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.tools import tool
from langchain.vectorstores import Pinecone


def playbook_chat(user_score: str):
    pinecone.init(os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENV"))

    def get_relevant_fragments(query: str) -> list[str]:
        docsearch = Pinecone.from_existing_index("playbook", OpenAIEmbeddings())
        docs = docsearch.similarity_search(query)
        return [doc.page_content for doc in docs]

    @tool
    def query_playbook(query: str) -> str:
        """Searches the People Managers guide for the query."""
        return "\n".join(get_relevant_fragments(query))

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    agent = initialize_agent(
        [query_playbook],
        ChatOpenAI(temperature=0.9, model="gpt-4"),
        AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory,
        verbose=True,
    )

    answer = agent.run(
        input=f"""Help the user by querying the playbook and answering their questions. \
The user is a People Manager at a company. \
You are a conversational AI.

The user has responded to questions regarding their remote work. \
Their score was calculated to {user_score}%.

Remote work readiness scale:
Low: 0-50%
Medium: 51-90%
High: 91-100%

You can use Markdown when replying.
"""
    )

    print(answer)

    while True:
        question = input("> ")
        answer = agent.run(input=question)
        print(answer)
