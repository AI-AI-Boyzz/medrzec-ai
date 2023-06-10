from dotenv import load_dotenv
from langchain.llms import OpenAI
from langchain.chains import ConversationChain, LLMChain
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.prompts.prompt import PromptTemplate

QUESTIONS = """
- What is the human's name?
- What is the weather like today where the human is?
- What is he human's favourite type of soup?"""

PROMPT_TEMPLATE = f"""
The AI wants to obtain answers to the following questions:
{QUESTIONS}
The AI is insistent on obtaining the answers and will prioritize asking questions
over answering.

Current conversation:
{{history}}
Human: {{input}}
AI:"""

SUMMARY_TEMPLATE = f"""
Based on the conversation, summarise the Human's answers to the following questions:
{QUESTIONS}

Conversation:
{{history}}"""


def main():
    load_dotenv()

    llm = OpenAI()
    memory = ConversationBufferMemory()
    conversation = ConversationChain(
        prompt=PromptTemplate(
            input_variables=["history", "input"], template=PROMPT_TEMPLATE
        ),
        llm=llm,
        memory=memory,
    )

    # It would be nice to have the conversation end on its own, when the LLM
    # thinks it's obtained all the answers. I'm guessing we would need an agent for that?
    # Not important, as this is just a dummy/demo example/prototype/proof of concept
    try:
        while True:
            response = conversation(input("> "))["response"]
            print(response)
    except (EOFError, KeyboardInterrupt):
        pass

    summary_prompt = PromptTemplate(input_variables=["history"], template=SUMMARY_TEMPLATE)
    summary_chain = LLMChain(llm=llm, prompt=summary_prompt)
    summary = summary_chain(memory.buffer)["text"]
    print(summary)


if __name__ == "__main__":
    main()
