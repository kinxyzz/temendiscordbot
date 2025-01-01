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

# Konfigurasi engine dengan parameter yang lebih robust
engine = create_engine(
    DATABASE_URL,
    pool_size=5,                    # Jumlah koneksi dalam pool
    max_overflow=10,                # Koneksi tambahan yang diizinkan
    pool_timeout=30,                # Timeout untuk mendapatkan koneksi
    pool_recycle=1800,             # Recycle koneksi setiap 30 menit
    pool_pre_ping=True,            # Cek koneksi sebelum digunakan
)

Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

@contextmanager
def get_session():
    session = SessionLocal()
    retry_count = 0
    max_retries = 3
    
    while retry_count < max_retries:
        try:
            yield session
            session.commit()
            break
        except OperationalError:
            session.rollback()
            retry_count += 1
            if retry_count == max_retries:
                raise
            # Buat koneksi baru
            session = SessionLocal()
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()

# Fungsi untuk operasi database dengan retry
async def db_operation(operation):
    try:
        with get_session() as session:
            return operation(session)
    except OperationalError as e:
        print(f"Database connection error: {e}")
        raise
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        raise
