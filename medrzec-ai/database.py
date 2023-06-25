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


engine = sqlalchemy.create_engine(os.environ["DATABASE_PATH"])
Base.metadata.create_all(engine)


def add_user(user: User):
    with Session(engine) as session:
        session.add(user)
        session.commit()


def get_user(email: str) -> User | None:
    with Session(engine) as session:
        return session.scalars(select(User).where(User.email == email)).first()


def delete_user(email: str) -> Result:
    with Session(engine) as session:
        return session.execute(delete(User).where(User.email == email))
