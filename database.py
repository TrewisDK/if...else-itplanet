from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
import os

url = os.environ["SPRING_DATASOURCE_URL"]
user = os.environ["POSTGRES_USER"]
password = os.environ["POSTGRES_PASSWORD"]

#SQLALCHEMY_DATABASE_URL = "postgresql://postgres:VfRFwObDDvvW@127.0.0.1/itplanet"
URL = f"{url}?user={user}&password={password}"
engine = create_engine(
    URL
)

Base = declarative_base()

SessionLocal = sessionmaker(autoflush=False, bind=engine)

