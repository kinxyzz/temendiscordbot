from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from contextlib import contextmanager
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")

engine = create_engine(
    DATABASE_URL,
    pool_size=10,           
    max_overflow=5,        
    pool_recycle=1800,
    pool_pre_ping=True
)

Base = declarative_base()
Session = sessionmaker(bind=engine)
