from __future__ import annotations

import os
from datetime import datetime

from sqlalchemy import ForeignKey, create_engine, delete, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from sqlalchemy.sql import func


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
    
    def add_purchase(self, user_id: int):
        with Session(self.engine) as session:
            session.add(Purchase(user_id=user_id))
            session.commit()

    def get_purchases(self, user_id: int) -> list[Purchase]:
        with Session(self.engine) as session:
            return session.scalars(select(Purchase).where(Purchase.user_id == user_id)).all()