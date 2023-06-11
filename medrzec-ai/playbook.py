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

PROMPT = PromptTemplate(
    input_variables=["question", "chat_history"],
    template="""System: The following is a conversation between a user and an AI. \
The user is a People Manager at a company. \
The AI finds asnwers to their questions by querying the playbook. \
It is conversational.

{chat_history}
Human: {question}
AI: """,
)


pinecone.init(os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENV"))


def get_relevant_fragments(query: str) -> list[str]:
    docsearch = Pinecone.from_existing_index("playbook", OpenAIEmbeddings())
    docs = docsearch.similarity_search(query)
    return [doc.page_content for doc in docs]


def playbook_chat():
    llm = ChatOpenAI(temperature=0.9)
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    docsearch = Pinecone.from_existing_index("playbook", OpenAIEmbeddings())
    qa = ConversationalRetrievalChain.from_llm(
        llm, docsearch.as_retriever(), memory=memory, verbose=True
    )

    while True:
        question = input("> ")
        answer = qa({"question": question})["answer"]
        print(answer)
