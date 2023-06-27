from __future__ import annotations

import os

import sqlalchemy
from sqlalchemy import Result, delete, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "email"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)


class Database:
    def __init__(self) -> None:
        self.engine = sqlalchemy.create_engine(os.environ["DATABASE_PATH"])
        Base.metadata.create_all(self.engine)

    def add_user(self, user: User):
        with Session(self.engine) as session:
            session.add(user)
            session.commit()

    def get_user(self, email: str) -> User | None:
        with Session(self.engine) as session:
            return session.scalars(select(User).where(User.email == email)).first()

    def delete_user(self, email: str) -> Result:
        with Session(self.engine) as session:
            return session.execute(delete(User).where(User.email == email))
