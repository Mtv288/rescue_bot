from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

from sqlalchemy import Column, Integer, String, Boolean

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, unique=True)
    name = Column(String)
    call_sign = Column(String)
    birth_year = Column(String)
    role = Column(String)
    approved = Column(Boolean, default=False)


class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    leader_id = Column(Integer, ForeignKey("users.id"))
    leader = relationship("User")

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    description = Column(String)
    completed = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
