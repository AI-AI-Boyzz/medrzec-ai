from dotenv import load_dotenv

from langchain.chat_models import ChatOpenAI
from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.agents import AgentType

QUESTIONS = [
    "How would you describe your role at your company?",
    "What is your most common work setup?",
    "How much can you relate to the following statement: I like working remotely.",
    "How much can you relate to the following statement: I'm able to disconnect from work mentally at the end of the day.",
    "How much can you relate to the following statement: I want to grow professionally and learn new skills at work.",
    "How much can you relate to the following statement: When I am assigned tasks, I can get them done easily as I am a self-starter and independent in my work habits.",
    "How much can you relate to the following statement: I feel I am effective at self-organizing my work.",
    "How much can you relate to the following statement: I feel that the course of my day depends on me.",
    "How much can you relate to the following statement: I can be productive anywhere - the place doesn't matter.",
    "How much can you relate to the following statement: I am easily able to manage projects remotely.",
    "How much can you relate to the following statement: I feel comfortable with running the team remotely.",
    "Imagine you need to ask your teammate a question about some project details. What do you do?",
    "Imagine you need to ask your employee a question about some project details. What do you do?",
    # TODO: This is just a placeholder, we probably shouldn't hardcode questions like this
]

NEWLINE = '\n'
OBJECTIVE = f"""
Find out the human's answers to the following questions:
{NEWLINE.join(QUESTIONS)}
When asking the human questions, be friendly and open to conversation. Do not ask
all questions at once. Try to rephrase questions or give up if the
human is not interested in answering."""


def main():
    load_dotenv()

    llm = ChatOpenAI(temperature=0.9)
    tools = load_tools(["human"])

    agent = initialize_agent(
        tools, llm, AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=True
    )

    answer = agent.run(OBJECTIVE)
    print(answer)


if __name__ == "__main__":
    main()
