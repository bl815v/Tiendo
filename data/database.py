"""Set up the SQLAlchemy database connection and session management.

Load environment variables using python-dotenv, retrieve the database URL,
and initialize the SQLAlchemy engine, session maker, and declarative base.
Provide a generator function for dependency-injected database sessions.

Attributes:
    DATABASE_URL (str): The database connection URL loaded from environment variables.
    engine (sqlalchemy.Engine): The SQLAlchemy engine instance.
    SessionLocal (sqlalchemy.orm.session.sessionmaker): Factory for database sessions.
    Base (sqlalchemy.ext.declarative.api.DeclarativeMeta): Base class for ORM models.

Functions:
    get_db(): Yields a database session for use in dependency injection, ensuring proper cleanup.

"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL is None:
	raise RuntimeError('DATABASE_URL environment variable is not set')

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
	"""
	Yield a SQLAlchemy database session.

	This function provides a database session for use in dependency injection,
	ensuring the session is properly closed after use.
	"""
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()
