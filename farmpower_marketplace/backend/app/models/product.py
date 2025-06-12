from sqlalchemy import Column, Integer, String, Float, JSON
from ..core.database import Base

class Tractor(Base):
    __tablename__ = "tractors"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    price = Column(Float)
    location = Column(String)
    image_url = Column(String, nullable=True)
    description = Column(String, nullable=True)
    specs = Column(JSON, nullable=True)

class Part(Base):
    __tablename__ = "parts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    price = Column(Float)
    location = Column(String)
    image_url = Column(String, nullable=True)
    description = Column(String, nullable=True)
    brand = Column(String, nullable=True)
    part_type = Column(String, nullable=True) 