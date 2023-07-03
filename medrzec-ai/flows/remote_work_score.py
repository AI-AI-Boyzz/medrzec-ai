import asyncio
import dataclasses
import math

from langchain.agents import AgentType, Tool, initialize_agent
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

from .flow import Flow


class AnswerException(Exception):
    pass


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

MIN_SCORE = sum(min(question.points) for question in LEADER_QUESTIONS)
MAX_SCORE = sum(max(question.points) for question in LEADER_QUESTIONS)


class RemoteWorkScoreChat(Flow):
    def __init__(self) -> None:
        super().__init__()

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

    async def start_conversation(self) -> str:
        return await self.next_question()

    async def submit_message(self, text: str) -> list[str]:
        question_index = len(self.answers)
        question = LEADER_QUESTIONS[question_index]
        available_answers = format_answers(question.answers)

        try:
            response = await asyncio.to_thread(
                self.response_parser.run,
                f"""\
You're a conversational AI agent designed to parse user's responses to a questionnaire regarding their remote work experience.

The user was asked: "{question.question}".

The possible answers are:
{available_answers}

The user's response was: "{text}".

If the answer makes sense, submit the number representing it to the question to the "submit_answer" function.

Reply with some feedback to the user. Use Markdown formatting. Add emojis.""",
            )
        except AnswerException as e:
            return [str(e)]

        messages = [response]

        if question_index + 1 >= len(LEADER_QUESTIONS):
            self.flow_end = True
            points = calculate_points(LEADER_QUESTIONS, self.answers)
            score = calculate_score(points, MIN_SCORE, MAX_SCORE)
            messages.append(
                f"You've got {points} points which results in "
                f"a {score}% Leader Remote Work Score."
            )
        elif not self.retry:
            messages.append(await self.next_question())

        return messages

    async def next_question(self) -> str:
        self.retry = True
        question_index = len(self.answers)
        question = LEADER_QUESTIONS[question_index]
        available_answers = format_answers(question.answers)

        return await self.question_asker.arun(
            question_number=question_index + 1,
            question_amount=len(LEADER_QUESTIONS),
            question=question.question,
            answers=available_answers,
        )

    def submit_answer(self, answer: str):
        try:
            answer_int = math.ceil(float(answer))
        except ValueError as e:
            raise AnswerException(
                f"{answer!r} is not a valid option. Try again."
            ) from e

        answers = LEADER_QUESTIONS[len(self.answers)].answers
        answers = 5 if answers is None else len(answers)

        if answer_int > answers or answer_int < 1:
            raise AnswerException(f"{answer} is not a valid option. Try again.")

        self.retry = False
        self.answers.append(answer_int - 1)


def format_answers(answers: list[str] | None) -> str:
    if answers is None:
        return "A single digit between 1 (not at all) and 5 (absolutely yes)"
    else:
        return "\n".join(f"{i}. {answer}" for i, answer in enumerate(answers, 1))


def calculate_points(questions: list[Question], answers: list[int]) -> int:
    return sum(
        question.points[answer]
        for question, answer in zip(questions, answers, strict=True)
    )


def calculate_score(points: int, min_points: int, max_points: int) -> int:
    score = (points - min_points) / (max_points - min_points)
    return math.ceil(score * 100)
