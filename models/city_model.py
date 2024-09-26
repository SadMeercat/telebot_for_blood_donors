from sqlalchemy import Column, Integer, String, func, select
from sqlalchemy.orm import relationship

from db.session import get_session, Base

class City(Base):
    __tablename__ = "cities"
    id = Column(Integer, primary_key=True)
    city_name = Column(String(100), nullable=False)

    hospitals = relationship("Hospital", back_populates="city")

def get_or_create_city(city_name:str):
    session = next(get_session())
    city = session.query(City).filter(func.lower(City.city_name) == func.lower(city_name)).first()
    if not city:
        city = City(city_name=city_name)
        session.add(city)
        session.commit()
    return city

def get_city_id(city_name):
    session = next(get_session())
    stmt = select(City.id).where(func.lower(City.city_name) == func.lower(city_name))
    city_id = session.execute(stmt).first()
    if not city_id:
        from db import find_similar_city
        possible_cities = find_similar_city(city_name)
        if len(possible_cities) > 0:
            return False, possible_cities
        else:
            return False, None
    else:
        return True, city_id.id