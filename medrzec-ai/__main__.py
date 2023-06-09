import dotenv
from langchain.llms import OpenAI


def main():
    dotenv.load_dotenv()

    llm = OpenAI()
    text = "What would be a good company name for a company that makes colorful socks?"
    print(llm(text))


if __name__ == "__main__":
    main()
