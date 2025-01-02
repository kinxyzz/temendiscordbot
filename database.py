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

# Engine dengan connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=10,           # Maksimal 10 koneksi dalam pool
    max_overflow=5,         # Koneksi tambahan jika pool penuh
    pool_recycle=1800,      # Daur ulang koneksi idle setelah 30 menit
    pool_pre_ping=True      # Cek kesehatan koneksi sebelum digunakan
)

Base = declarative_base()
Session = sessionmaker(bind=engine)