from sqlalchemy import create_engine # type: ignore
from sqlalchemy.ext.declarative import declarative_base # type: ignore
from sqlalchemy.orm import sessionmaker # type: ignore
from dotenv import load_dotenv # type: ignore
import os

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")


engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()

session = SessionLocal()