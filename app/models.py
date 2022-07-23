from sqlalchemy import JSON, Column, Integer, String
from .database import Base

class Networks(Base):
    __tablename__ = 'networks'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30), unique=True, index=True)
    vpc_id = Column(String(30), unique=True, index=True)
    plan_id = Column(Integer, unique=True, index=True)
    plan_state = Column(String(30), unique=True, index=True)
    tf_state = Column(JSON)
    payload = Column(JSON)

class Plans(Base):
    __tablename__ = 'plans'

    id = Column(Integer, primary_key=True, index=True)
    plan = Column(String(30), unique=True, index=True)

class Locks(Base):
    __tablename__ = 'locks'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30), unique=True, index=True)
    