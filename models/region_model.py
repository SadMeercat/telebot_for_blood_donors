from sqlalchemy import Column, Integer, String, func, select
from sqlalchemy.orm import relationship

from db.session import get_session, Base

class Region(Base):
    __tablename__ = "regions"
    id = Column(Integer, primary_key=True)
    region_name = Column(String(100), nullable=False)

    hospital = relationship("Hospital", back_populates="region")

def get_or_create_region(region_name:str):
    session = next(get_session())
    region = session.query(Region).filter(func.lower(Region.region_name) == func.lower(region_name)).first()
    if not region:
        region = Region(region_name=region_name)
        session.add(region)
        session.commit()
    return region
