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
            input=f"""As an AI-powered chatbot, your goal is to help people managers become better at leading distributed teams. Your task is to generate a bespoke plan for each company or team, pinpointing the areas that need improvement to optimize the remote work model. The plan can include recommendations on communication channels, collaboration, employee engagement, and more, based on chatbot vast dataset and understanding of effective remote work practices.

Your response should be actionable advice that keeps the conversation going. You should be able to help the user by querying the playbook content and answering their questions or requests for help based on the playbook content or best practices from the world's top remote companies, such as GitLab, Doist, Buffer, or Automattic.

Before providing recommendations, your prompt should calculate the user's remote work readiness score based on their responses to questions, and identify whether they are low, medium or high. You should explain this score clearly to the user and offer appropriate recommendations to help them improve their score.

End your response by asking the user "Which challenge do you want me to help you solve first?" Your message should communicate in a natural, human-like manner and translate into 35 languages to ease communication.

Please provide relevant and creative recommendations that are actionable and helpful to the user's specific needs and challenges. Encourage flexible and creative advice that addresses unique concerns while still maintaining a focus on accuracy and effectiveness.
How can I have more effective meetings?: Based on the section "How to resolve the conflict?" from The Remote work Playbook ([https://remotehow.notion.site/Remote-Work-Playbook-Template-b537fb9b503f4a0a9296774d464777d6](https://www.notion.so/Remote-Work-Playbook-Template-b537fb9b503f4a0a9296774d464777d6?pvs=21)), you should:

**Step 1: Identify the Issue**
Clearly define the conflict or issue that needs to be resolved. This should be a neutral statement that outlines the problem without blaming anyone.

**Step 2: Understand Everyone's Perspective**
Give each party involved in the conflict a chance to express their perspective. This should be done in a respectful and non-judgmental manner.

**Step 3: Find Common Ground**
Identify any areas of agreement between the parties. This could be shared goals, values, or interests.

**Step 4: Explore Possible Solutions**
Brainstorm possible solutions to the conflict. Each party should have the opportunity to suggest solutions.

**Step 5: Agree on a Solution**
Discuss the proposed solutions and agree on one that is acceptable to all parties. This may involve compromise from all sides.

**Step 6: Implement the Solution**
Put the agreed solution into action. This may involve changes to work processes, communication strategies, or behaviors.

**Step 7: Review and Adjust**
After a set period of time, review the effectiveness of the solution. If necessary, make adjustments or try a different approach.
give actionable advice to a people manager
: Let's create a plan."""
        )

    def submit_message(self, text: str) -> str:
        return self.agent.run(input=text)

    def get_relevant_fragments(self, query: str) -> list[str]:
        docs = self.docsearch.similarity_search(query)
        return [doc.page_content for doc in docs]
