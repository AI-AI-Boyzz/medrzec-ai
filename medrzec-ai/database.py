import enum
import os

import sqlalchemy
from sqlalchemy import Enum, Result, delete, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Role(enum.Enum):
    user = 1
    admin = 2


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "email"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    role: Mapped[Enum] = mapped_column(Enum(Role))


class APIKey(Base):
    __tablename__ = "api_key"
    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str]


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


def add_api_key(api_key: APIKey):
    with Session(engine) as session:
        session.add(api_key)
        session.commit()


def get_api_key(key: str) -> APIKey | None:
    with Session(engine) as session:
        return session.scalars(select(APIKey).where(APIKey.key == key)).first()


def delete_api_key(key: str) -> Result:
    with Session(engine) as session:
        return session.execute(delete(APIKey).where(APIKey.key == key))
