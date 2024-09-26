from sqlalchemy import Column, Integer, String, func, select
from sqlalchemy.orm import relationship

from db.session import get_session, Base

class Region(Base):
    __tablename__ = "regions"
    id = Column(Integer, primary_key=True)
    region_name = Column(String(100), nullable=False)

    hospitals = relationship("Hospital", back_populates="region")

def get_or_create_region(region_name:str):
    session = next(get_session())
    region = session.query(Region).filter(func.lower(Region.region_name) == func.lower(region_name)).first()
    if not region:
        region = Region(region_name=region_name)
        session.add(region)
        session.commit()
    return region

def get_region_id(region_name):
    session = next(get_session())
    stmt = select(Region.id).where(func.lower(Region.region_name) == func.lower(region_name))
    region_id = session.execute(stmt).first()
    if not region_id:
        from db import find_similar_region
        possible_cities = find_similar_region(region_name)
        if len(possible_cities) > 0:
            return False, possible_cities
        else:
            return False, None
    else:
        return True, region_id.id
