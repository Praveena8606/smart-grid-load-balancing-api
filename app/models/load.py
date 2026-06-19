from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Load(Base):
    __tablename__ = "loads"

    id = Column(Integer, primary_key=True, index=True)
    area = Column(String, nullable=False)
    current_load = Column(Float, nullable=False)
    max_capacity = Column(Float, nullable=False)