import dataclasses
import math

from langchain.agents import AgentType, Tool, initialize_agent
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

from .flow import Flow


@dataclasses.dataclass
class Question:
    question: str
    answers: list[str] | None = None
    points: list[int] = dataclasses.field(default_factory=lambda: list(range(-2, 3)))


LEADER_QUESTIONS = [
    Question(
        "How easily are you able to **manage projects** remotely?",
    ),
    Question(
        "How comfortable do you feel with **running the team** remotely?",
    ),
    Question(
        "Your **team's work effectiveness** is:",
        ["Better at the office", "No difference", "Better remotely"],
        [-2, 0, 2],
    ),
    Question(
        "Our **team habits** include:",
        [
            "Celebrate successes together (eg. completing the project)",
            "Hang out and talk about non-work-related topics",
            "Meet in-person for special team building events",
            "Organize personal events, e.g. volunteer actions, birthdays celebration",
            "None of the above",
        ],
        [1, 1, 1, 1, 0],
    ),
    Question(
        "Do you think everyone on your team **feels included**?",
    ),
    Question(
        "Do you have access to proper **training on how to manage a team remotely**?"
    ),
    Question(
        "Can you share **honest feedback with people you report to** which you discuss and action is taken?",
    ),
    Question(
        "Do you receive clear information from people you report to about **what your and your team's tasks are**?",
    ),
    Question(
        "Can you **share honest feedback to your team employees** and have an open discussion about it?"
    ),
    Question(
        "Do you give clear information to people in your team about **what their tasks are**?"
    ),
    Question("Do you know **how your employees feel** even when you work remotely?"),
]


class RemoteWorkScoreChat(Flow):
    def __init__(self) -> None:
        self.answers: list[int] = []
        self.retry = False

        llm = ChatOpenAI(temperature=1, model="gpt-4", client=None)

        self.question_asker = LLMChain(
            llm=llm,
            prompt=PromptTemplate(
                input_variables=[
                    "question_number",
                    "question_amount",
                    "question",
                    "answers",
                ],
                template="""\
You're a conversational AI agent designed to ask user questions regarding their remote work experience.

Question {question_number} of {question_amount}:
{question}

Possible answers:
{answers}

Ask the question and provide the possible answers. Use Markdown formatting. Add emojis.""",
            ),
        )

        self.response_parser = initialize_agent(
            [
                Tool(
                    name="submit_answer",
                    func=self.submit_answer,
                    description="submit user's answer to the question",
                ),
            ],
            llm,
            agent=AgentType.OPENAI_FUNCTIONS,
        )

    def start_conversation(self) -> str:
        return self.next_question()

    def submit_message(self, text: str) -> list[str]:
        question_index = len(self.answers)
        question = LEADER_QUESTIONS[question_index]
        available_answers = format_answers(question.answers)

        response = self.response_parser.run(
            f"""\
You're a conversational AI agent designed to parse user's responses to a questionnaire regarding their remote work experience.

The user was asked: "{question.question}".

The possible answers are:
{available_answers}

The user's response was: "{text}".

If the answer makes sense, submit the number representing it to the question to the "submit_answer" function.

Reply with some feedback to the user. Use Markdown formatting. Add emojis."""
        )

        messages = [response]

        if question_index >= len(LEADER_QUESTIONS):
            points = calculate_points(LEADER_QUESTIONS, self.answers)
            score = calculate_score(points, -20, 21)
            messages.append(
                f"You've got {points} points which results in "
                f"a {score}% Leader Remote Work Score."
            )
        elif not self.retry:
            messages.append(self.next_question())

        return messages

    def next_question(self) -> str:
        self.retry = True
        question_index = len(self.answers)
        question = LEADER_QUESTIONS[question_index]
        available_answers = format_answers(question.answers)

        return self.question_asker.run(
            question_number=question_index + 1,
            question_amount=len(LEADER_QUESTIONS),
            question=question.question,
            answers=available_answers,
        )

    def submit_answer(self, answer: str):
        self.retry = False
        self.answers.append(int(answer))


def format_answers(answers: list[str] | None) -> str:
    if answers is None:
        return "An integer between 1 (not at all) and 5 (absolutely yes)"
    else:
        return "\n".join(f"{i}. {answer}" for i, answer in enumerate(answers, 1))


def calculate_points(questions: list[Question], answers: list[int]) -> int:
    return sum(
        question.points[answer - 1]
        for question, answer in zip(questions, answers, strict=True)
    )


def calculate_score(points: int, min_points: int, max_points: int) -> int:
    return math.ceil(((points - min_points) / -min_points + max_points) * 100)
