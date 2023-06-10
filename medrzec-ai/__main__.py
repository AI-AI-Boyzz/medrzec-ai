from dotenv import load_dotenv
from langchain.llms import OpenAI
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.prompts.prompt import PromptTemplate

PROMPT_TEMPLATE = """
The following is a friendly conversation between a human and an AI.
The AI is talkative and provides lots of specific details from its context.
If the AI does not know the answer to a question, it truthfully says it does not know.

Importantly, the AI wants to obtain answers to the following questions:
- What is the human's name?
- What is the weather like today where the human is?
- What is he human's favourite type of soup?

Current conversation:
{history}
Human: {input}
AI:"""


def main():
    load_dotenv()

    llm = OpenAI()
    conversation = ConversationChain(
        prompt=PromptTemplate(
            input_variables=["history", "input"], template=PROMPT_TEMPLATE
        ),
        llm=llm,
        memory=ConversationBufferMemory(),
    )

    while True:
        response = conversation(input("> "))["response"]
        print(response)


if __name__ == "__main__":
    main()
