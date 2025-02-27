from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from pkg.config import settings

engine = create_engine(url=settings.DATABASE_URL)
session_factory = sessionmaker(engine)

Base = declarative_base()


def create_db():
    Base.metadata.create_all(engine)


def drop_db():
    Base.metadata.drop_all(engine)
