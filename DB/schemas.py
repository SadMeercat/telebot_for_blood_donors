from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Region(Base):
    __tablename__ = "regions"
    id = Column(Integer, primary_key=True)
    region_name = Column(String(100), nullable=False)

    hospital = relationship("Hospital", back_populates="region")

class City(Base):
    __tablename__ = "cities"
    id = Column(Integer, primary_key=True)
    city_name = Column(String(100), nullable=False)

    hospital = relationship("Hospital", back_populates="city")

class District(Base):
    __tablename__ = "districts"
    id = Column(Integer, primary_key=True)
    district_name = Column(String(100), nullable=False)

    hospital = relationship("District", back_populates="district")


class Hospital(Base):
    __tablename__ = "hospitals"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    region_id = Column(Integer, ForeignKey("regions.id"))
    city_id = Column(Integer, ForeignKey("cities.id"))
    district_id = Column(Integer, ForeignKey("districts.id"))
    address = Column(String(100))
    url_address = Column(String(100))

    user = relationship("User", back_populates="hospital")
    region = relationship("Region", back_populates="region")
    city = relationship("City", back_populates="city")
    district = relationship("District", back_populates="district")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, nullable=False)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"))
    last_donation = Column(Date())

    hospital = relationship("Hospital", back_populates="user")
