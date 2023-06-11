from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import AIMessage, HumanMessage, SystemMessage

PREDEFINED_MESSAGES = [
    SystemMessage(
        content="""\
Do not reply instead of the user (don't use the "Human: " message prefix)."""
    ),
    HumanMessage(
        content="""\
We are building an AIwo, a powerful agent to help managers make data-driven decisions about work organization changes they need to implement. Our product includes a Remote Work Score, a personalized AI-powered Improvements Plan, and a personalized AI-powered Playbook creation.
AIwo is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, AIwo is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.
AIwo is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, AIwo is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.
Overall, AIwo is a powerful tool that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, AIwo is here to assist."""
    ),
    AIMessage(
        content="""\
Here's a further outline of the product, detailing some more specifics of the individual components you mentioned.
Remote Work Score: The Remote Work Score provides a quantitative assessment of how well a company or team is adapting to the remote work model. This score is generated based on a multitude of factors, including productivity metrics, employee engagement and satisfaction surveys, collaboration efficiency, and the effectiveness of communication channels. It serves as a straightforward indicator of a company's remote work performance, which managers can use to gauge their success and identify areas that need improvement.
Personalized AI-powered Improvements Plan: AIwo generates a bespoke plan for each company or team, pinpointing the areas that need enhancement to optimize the remote work model. The plan can include recommendations on improving communication channels, facilitating better collaboration, enhancing employee engagement, and more. These suggestions are based on AIwo's vast dataset and understanding of effective remote work practices.
Personalized AI-powered Playbook creation: Based on the Improvement Plan, AIwo helps in the creation of a personalized playbook. This playbook acts as a comprehensive guide for managers to implement the suggested changes. It includes detailed steps, potential challenges and their solutions, timelines, and success metrics. The AI constantly learns from the outcomes and adapts the playbook accordingly, making it a living document that evolves with the needs of the team.
AIwo can potentially revolutionize how companies handle remote work, offering key insights and practical solutions driven by AI and robust data analytics. By assisting in data-driven decision making and providing actionable recommendations, AIwo can help managers optimize their team's productivity and satisfaction in a remote work environment."""
    ),
    HumanMessage(
        content="""\
Can you act as AIwo and start asking me questions to assess my remote work conditions?
Ask me 10 questions one by one.
Please ensure the questions cover all work-related aspects from this list of areas: Communication, Collaboration, Leadership, Job Satisfaction, Company Culture, Transparency, Well-being, Adaptation, Work management.
After I answer your questions, can you help me compute a score from 0-100 based on my responses?
Please output it in the following format: "Score: <score>."""
    ),
]

FINAL_HUMAN_MESSAGE = "Start by asking the first question now."


class QuestionChat:
    def __init__(self) -> None:
        llm = ChatOpenAI(temperature=1, model="gpt-4")
        memory = ConversationBufferMemory()
        memory.chat_memory.messages.extend(PREDEFINED_MESSAGES)
        self.chain = ConversationChain(llm=llm, memory=memory, verbose=True)

    def start_conversation(self) -> str:
        return self.chain(FINAL_HUMAN_MESSAGE)["response"]

    def submit_message(self, text: str) -> str:
        return self.chain(text)["response"]
