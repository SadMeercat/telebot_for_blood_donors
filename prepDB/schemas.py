from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Hospital(Base):
    __tablename__ = "hospitals"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    region = Column(String(100))
    city = Column(String(100))
    district = Column(String(100))
    address = Column(String(100))
    url_address = Column(String(100))

    user = relationship("User", back_populates="hospital")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, nullable=False)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"))
    last_donation = Column(Date())

    hospital = relationship("Hospital", back_populates="user")
