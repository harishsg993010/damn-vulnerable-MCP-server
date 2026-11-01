import os
from datetime import datetime

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Float,
    Text,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "dvmcp.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency that provides a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    submissions = relationship("Submission", back_populates="user")
    progress = relationship("Progress", back_populates="user")
    hint_usages = relationship("HintUsage", back_populates="user")
    analytics_events = relationship("AnalyticsEvent", back_populates="user")


class PlayerSlot(Base):
    """Maps a user to a dedicated challenge container in the pool.

    Each slot corresponds to one container running its own copy of the 15
    challenge servers, so players never share mutable challenge state.
    """

    __tablename__ = "player_slots"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    slot = Column(Integer, unique=True, nullable=False, index=True)
    assigned_at = Column(DateTime, default=datetime.utcnow)


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    challenge_id = Column(Integer, nullable=False)
    flag = Column(String(255), nullable=False)
    is_correct = Column(Boolean, default=False)
    points_awarded = Column(Integer, default=0)
    submitted_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="submissions")


class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    challenge_id = Column(Integer, nullable=False)
    status = Column(String(20), default="not_started")  # not_started / in_progress / completed
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="progress")


class HintUsage(Base):
    __tablename__ = "hint_usages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    challenge_id = Column(Integer, nullable=False)
    hint_level = Column(Integer, nullable=False)  # 1, 2, or 3
    points_cost = Column(Integer, nullable=False)
    used_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="hint_usages")


class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    event_type = Column(String(50), nullable=False)
    challenge_id = Column(Integer, nullable=True)
    data_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="analytics_events")


def init_db():
    """Create all tables in the database."""
    Base.metadata.create_all(bind=engine)
