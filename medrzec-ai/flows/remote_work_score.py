import asyncio
import dataclasses
import math
from enum import Enum, auto

from fastapi import HTTPException
from langchain.agents import AgentType, Tool, initialize_agent
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from ..utils import text_utils
from ..utils.text_utils import TextFormat, ChatMemory
from .flow import Flow, FlowResponse


class AnswerException(Exception):
    pass


class TeamRoles(Enum):
    TEAM_MEMBER = auto()
    PEOPLE_LEADER = auto()


@dataclasses.dataclass
class Question:
    question: str
    answers: list[str] | None = None
    points: list[int] = dataclasses.field(default_factory=lambda: [-2, -1, 0, 1, 2])


def get_questions(role: TeamRoles, text_format: TextFormat) -> list[Question]:
    questions = [
        Question(
            "What is your **most common work setup**?",
            [
                "100% from the office",
                "Mix remote & office (mandate days)",
                "Mix remote & office (full flexibility)",
                "100% remotely",
                "Other",
            ],
            [0] * 5,
        ),
        Question("Do you **like working remotely**?"),
        Question(
            "Are you able to **disconnect from work mentally** at the end of the day?"
        ),
        Question(
            "Do you want to **grow professionally and learn** new skills at work?"
        ),
        Question(
            "When someone assignes you tasks, can you **get them done easily**, "
            "because you're a self-starter and independent in your work habits?",
        ),
        Question("Do you feel you're **effective at self-organizing** your work?"),
        Question("Do you feel that **the course of your day depends on you**?"),
        Question("Can you be **productive anywhere** — the place doesn't matter?"),
    ]

    if role is TeamRoles.PEOPLE_LEADER:
        questions.extend(
            [
                Question("Can you easily **manage projects** remotely?"),
                Question("Do you **feel comfortable running the team** remotely?"),
            ]
        )

    if role is not TeamRoles.PEOPLE_LEADER:
        questions.append(
            Question(
                "Imagine you need to **ask your teammate a question** about some project details. "
                "What do you do?",
                [
                    "I grab the phone and have a **quick call**",
                    "I catch them on a **chat** (e.g. Teams or Slack) ",
                    "I send them an **email**",
                    "I schedule a **short meeting**",
                    "I don't like to bother others - "
                    "I try to find the answer by myself **in project files**.",
                ],
                [-1, 1, 1, -1, 1],
            )
        )

    if role is TeamRoles.PEOPLE_LEADER:
        questions.append(
            Question(
                "Imagine you need to **ask your employee a question** about some project details. "
                "What do you do?",
                [
                    "I grab the phone and have a **quick call**",
                    "I catch them on a **chat** (e.g. Teams or Slack) ",
                    "I send them an **email**",
                    "I schedule a **short meeting**",
                    "I don't like to bother others - "
                    "I try to find the answer by myself **in project files**.",
                ],
                [-1, 1, 1, -1, 1],
            )
        )

    questions.extend(
        [
            Question(
                "When you **write messages**, you always:",
                [
                    "Add all the necessary information to provide full context",
                    "Make sure it has the right tone so recipients feel respected and included",
                    "Include Call-to-Action with clear deadline",
                    "Use bolded fonts and some other font distinctions",
                    "None of above",
                ],
                [1, 1, 1, 1, 0],
            ),
            Question(
                "Final versions of **your files** are kept:",
                [
                    "On my computer desktop only",
                    "In folders on my laptop's hard drive",
                    "In the cloud, grouped in folders that my team has access to",
                    "In project documents/channels, e.g. on Notion, Teams",
                ],
                [-1, 0, 1, 1],
            ),
            Question(
                "When I **organize a meeting**, I:",
                [
                    "Double check if the meeting is needed, or if it could be done asynchronously",
                    "Add details to the invite incl. agenda, participants roles, goals",
                    "Share a collaborative document to review before the meeting",
                    "Assign roles to each participant",
                    'Take notes and add "to-do\'s" during the meeting',
                    "Send a written summary after the meeting to all stakeholders giving time for everyone to give feedback.",
                    "None of above",
                ],
                [1, 1, 1, 1, 1, 1, 0],
            ),
            Question(
                "For the bulk of my daily tasks, I prefer to work:",
                ["At the office", "No difference", "Remotely"],
                [-2, 0, 2],
            ),
            Question(
                'I can easily access a **"single source of truth"** '
                "with all operational information (documents, policies, announcements, etc.)"
            ),
            Question(
                "I **spend weekly X% of my time** in meetings.",
                ["up to 10%", "11%-25%", "26%-50%", "51%-75%", "more than 75%"],
                [2, 1, 0, -1, -2],
            ),
            Question(
                "**Active engagement in meetings** is:",
                ["Better at the office", "No different", "Better remotely"],
                [-2, 0, 2],
            ),
            Question(
                "**Learning new tasks and skills** is:",
                ["Better at the office", "No different", "Better remotely"],
                [-2, 0, 2],
            ),
            Question(
                "I had **training** that helped me **work remotely effectively**."
            ),
            Question(
                "I have clear and **agreed-upon metrics** that are tied to my ongoing job performance.",
                ["Yes", "No"],
                [1, 0],
            ),
        ]
    )

    if role is TeamRoles.PEOPLE_LEADER:
        questions.append(
            Question(
                "My **team's work effectiveness** is:",
                ["Better at the office", "No different", "Better remotely"],
                [-2, 0, 2],
            )
        )

    questions.extend(
        [
            Question(
                "My **team has clear rules** on how we:",
                [
                    "**Work together** (eg. when do we work, how do we collaborate, how do we plan work, etc.)",
                    "**Communicate** (e.g. when to communicate synchronously vs asynchronously, what tools to use, etc.)",
                    "**Run meetings** (e.g. when and how to schedule, checklist - before, during, after)",
                    "**Manage information** (e.g. documenting knowledge about projects, internal processes, etc.)",
                    "None of the above",
                ],
                [1, 1, 1, 1, 0],
            ),
            Question(
                "Our team habits include:",
                [
                    "**Celebrate successes** together (eg. completing the project)",
                    "**Hang out** and talk about non-work-related topics",
                    "**Meet in-person** for special team building events",
                    "**Organize personal events**, e.g. volunteer actions, birthdays celebration",
                    "None of the above",
                ],
                [1, 1, 1, 1, 0],
            ),
            Question("I think there is **transparency in communication** on my team."),
            Question(
                "I think there is **transparency in decision-making** on my team."
            ),
        ]
    )

    if role is not TeamRoles.PEOPLE_LEADER:
        questions.extend(
            [
                Question(
                    "I feel that **my team/project leader knows how to manage a distributed team**."
                ),
                Question(
                    "I can **share honest feedback with leadership**, which we discuss and action is taken."
                ),
                Question(
                    "I receive clear information from my team/project leader about **what my tasks are**."
                ),
            ]
        )

    questions.extend(
        [
            Question("I **trust** the people on my team."),
            Question("I feel like a **valuable member** of my team."),
        ]
    )

    if role is TeamRoles.PEOPLE_LEADER:
        questions.extend(
            [
                Question("I think everyone on my team **feels included**."),
                Question(
                    "I have access to proper **training on how to manage team remotely**."
                ),
                Question(
                    "I can **share honest feedback with people I report to** which we discuss and action is taken."
                ),
                Question(
                    "I receive clear information from people I report to about **what my team's and my tasks are**."
                ),
                Question(
                    "I **share honest feedback to my team employees** and have an open discussion about it."
                ),
                Question(
                    "I give clear information to people in my team about **what their tasks are**."
                ),
                Question("I know **how my employees feel** even when I work remotely."),
            ]
        )

    return questions


class RemoteWorkScoreChat(Flow):
    def __init__(self, role: TeamRoles, text_format: TextFormat) -> None:
        self.text_format = text_format

        self.questions = get_questions(role, text_format)
        self.answers: list[int] = []
        self.retry = False
        self.memory = ChatMemory(max_size=10)

        llm = ChatOpenAI(temperature=1, model="gpt-4", client=None)

        self.question_asker = LLMChain(
            llm=llm,
            prompt=PromptTemplate(
                input_variables=[
                    "question_number",
                    "question_amount",
                    "question",
                    "answers",
                    "history",
                ],
                template="""\
You're a conversational AI agent designed to ask user questions regarding their remote work experience.

Previously asked questions for reference:
{history}

Question {question_number} of {question_amount}:
{question}

Possible answers:
{answers}

Ask the question and provide the possible answers. Use Markdown formatting and add emojis.

AI: """,
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

    async def start_conversation(self) -> FlowResponse[str]:
        response = await self.next_question()
        return FlowResponse(response)

    async def submit_message(self, text: str) -> FlowResponse[list[str]]:
        question_index = len(self.answers)
        question = self.questions[question_index]
        available_answers = format_answers(question.answers)

        try:
            response = await asyncio.to_thread(
                self.response_parser.run,
                f"""\
You're a conversational AI agent designed to parse user's responses to a questionnaire regarding their remote work experience.

Previously asked questions for reference:
{self.memory.format_history()}

The user was asked: "{question.question}".

The possible answers are:
{available_answers}

The user's response was: "{text}".

If the answer makes sense, submit the number representing it to the question to the "submit_answer" function.

Reply with some feedback to the user. Use Markdown formatting and add emojis.

AI: """,
            )
        except AnswerException as e:
            raise HTTPException(400, str(e)) from e

        flow_end: bool = False
        score: int | None = None
        messages: list[str] = [response]

        if question_index + 1 >= len(self.questions):
            flow_end = True
            score = calculate_score(self.questions, self.answers)
            messages.append(
                text_utils.remote_work_score_message(score, self.text_format)
            )
        elif not self.retry:
            self.memory.add_human_message(text)
            messages.append(await self.next_question())

        return FlowResponse(
            messages,
            flow_suggestions=[] if flow_end else None,
            extra={"remote_work_score": score} if score is not None else {},
        )

    async def next_question(self) -> str:
        self.retry = True
        question_index = len(self.answers)
        question = self.questions[question_index]
        available_answers = format_answers(question.answers)

        response = await self.question_asker.arun(
            question_number=question_index + 1,
            question_amount=len(self.questions),
            question=question.question,
            answers=available_answers,
            history=self.memory.format_history(),
        )

        self.memory.add_ai_message(response)
        return response

    def submit_answer(self, answer: str) -> None:
        try:
            answer_int = math.ceil(float(answer))
        except ValueError as e:
            raise AnswerException(
                f"{answer!r} is not a valid option. Try again."
            ) from e

        answers = self.questions[len(self.answers)].answers
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


def calculate_score(questions: list[Question], answers: list[int]) -> int:
    min_points = sum(min(question.points) for question in questions)
    max_points = sum(max(question.points) for question in questions)

    points = sum(
        question.points[answer]
        for question, answer in zip(questions, answers, strict=True)
    )

    score = (points - min_points) / (max_points - min_points)
    return math.ceil(score * 100)
