from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:VfRFwObDDvvW@127.0.0.1/itplanet"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

Base = declarative_base()

SessionLocal = sessionmaker(autoflush=False, bind=engine)

