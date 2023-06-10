from dotenv import load_dotenv
from langchain.llms import OpenAI
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferMemory


def main():
    load_dotenv()

    llm = OpenAI()
    conversation = ConversationChain(
        llm=llm,
        memory=ConversationBufferMemory(),
    )

    while True:
        response = conversation(input("> "))["response"]
        print(response)


if __name__ == "__main__":
    main()
