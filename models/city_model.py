from sqlalchemy import Column, Integer, String, func, select
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from db.session import get_session, Base

class City(Base):
    __tablename__ = "cities"
    id = Column(Integer, primary_key=True)
    city_name = Column(String(100), nullable=False)

    hospital = relationship("Hospital", back_populates="city")

def get_or_create_city(city_name:str):
    session = next(get_session())
    city = session.query(City).filter(func.lower(City.city_name) == func.lower(city_name)).first()
    if not city:
        city = City(city_name=city_name)
        session.add(city)
        session.commit()
    return city