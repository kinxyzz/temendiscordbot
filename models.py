from sqlalchemy import Column, Integer, Text, text # type: ignore
from sqlalchemy.dialects.postgresql import TIMESTAMP # type: ignore
from database import Base # type: ignore

class UserScore(Base):
    __tablename__ = 'UserScore'

    id = Column(Text, primary_key=True)
    userId = Column(Text, nullable=False, unique=True)
    score = Column(Integer, nullable=False)
    createdAt = Column(TIMESTAMP(precision=3), nullable=False, server_default=text("CURRENT_TIMESTAMP"))