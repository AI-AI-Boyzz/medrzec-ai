from dotenv import load_dotenv

from langchain.chat_models import ChatOpenAI
from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.agents import AgentType

QUESTIONS = [
    "How would you describe your role at your company?",
    "What is your most common work setup?",
    "How much can you relate to the following statement: I like working remotely.",
    # TODO: This is just a placeholder, we probably shouldn't hardcode questions like this
]

NEWLINE = "\n"
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
