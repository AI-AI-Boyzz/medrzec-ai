from __future__ import annotations

import os
from datetime import datetime
from typing import List

from sqlalchemy import ForeignKey, create_engine, delete, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from sqlalchemy.sql import func

from medrzec_ai.agents.sales.data import InterviewTopic


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    country: Mapped[str] = mapped_column(nullable=False)
    industry: Mapped[str] = mapped_column(nullable=False)
    profession: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )


class RemoteWorkScore(Base):
    __tablename__ = "remote_work_score"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    score: Mapped[int] = mapped_column(nullable=False)
    type: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )


class Answer(Base):
    __tablename__ = "answer"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    question: Mapped[str] = mapped_column(nullable=False)
    response: Mapped[str] = mapped_column(nullable=False)
    topic: Mapped[InterviewTopic] = mapped_column(nullable=True)
    score: Mapped[float] = mapped_column(nullable=False)
    magnitude: Mapped[float] = mapped_column(nullable=False)


class Purchase(Base):
    __tablename__ = "purchase"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )


class Database:
    def __init__(self) -> None:
        self.engine = create_engine(os.environ["DATABASE_PATH"])
        Base.metadata.create_all(self.engine)

    def add_user(self, user: User):
        with Session(self.engine) as session:
            session.add(user)
            session.commit()

    def get_user(self, email: str) -> User | None:
        with Session(self.engine) as session:
            return session.scalars(select(User).where(User.email == email)).first()

    def delete_user(self, email: str):
        with Session(self.engine) as session:
            session.execute(delete(User).where(User.email == email))

    def add_answer(self, answer: Answer):
        with Session(self.engine) as session:
            session.add(answer)
            session.commit()

    def add_purchase(self, user_id: int):
        with Session(self.engine) as session:
            session.add(Purchase(user_id=user_id))
            session.commit()

    def get_purchases(self, user_id: int) -> list[Purchase]:
        with Session(self.engine) as session:
            return session.scalars(
                select(Purchase).where(Purchase.user_id == user_id)
            ).all()

    def get_score(self, user: User) -> int:
        with Session(self.engine) as session:
            elo = session.scalars(
                select(Answer)
                .where(Answer.user_id == user.id)
                .where(Answer.topic is not None)
                .group_by(Answer.topic)
            ).all()

            organization = [x for x in elo if x.topic == InterviewTopic.ORGANIZATION]
            comunication = [x for x in elo if x.topic == InterviewTopic.COMMUNICATION]
            leadership = [x for x in elo if x.topic == InterviewTopic.LEADERSHIP]
            culture = [x for x in elo if x.topic == InterviewTopic.CULTURE_AND_VALUES]
            welbeing = [x for x in elo if x.topic == InterviewTopic.WELLBEING]

            organizationScore = sum(
                map(lambda x: points_from_score(x.score), organization)
            ) / ((len(organization)) * 5)

            comunicationScore = sum(
                map(lambda x: points_from_score(x.score), comunication)
            ) / ((len(comunication)) * 5)

            leadershipScore = sum(
                map(lambda x: points_from_score(x.score), leadership)
            ) / ((len(leadership)) * 5)

            if (len(welbeing)) == 0:
                welbeingScore = 0
            else:
                welbeingScore = sum(
                    map(lambda x: points_from_score(x.score), welbeing)
                ) / ((len(welbeing)) * 5)

            if len(culture) == 0:
                cultureScore = 0
            else:
                cultureScore = sum(
                    map(lambda x: points_from_score(x.score), cultureScore)
                ) / ((len(culture)) * 5)

            score = (
                (
                    organizationScore
                    + comunicationScore
                    + leadershipScore
                    + welbeingScore
                    + cultureScore
                )
                / 5
                * 100
            )

            return int(score)


def points_from_score(score: float):
    if score < -0.6:
        return 1
    if score < -0.2:
        return 2
    if score < 0.2:
        return 3
    if score < 0.6:
        return 4
    return 5
