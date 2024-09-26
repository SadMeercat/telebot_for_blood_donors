from sqlalchemy import Column, Integer, String, func, select
from sqlalchemy.orm import relationship


from db.session import get_session, Base

class District(Base):
    __tablename__ = "districts"
    id = Column(Integer, primary_key=True)
    district_name = Column(String(100), nullable=False)

    hospitals = relationship("Hospital", back_populates="district")

def get_or_create_district(district_name:str):
    session = next(get_session())
    district = session.query(District).filter(func.lower(District.district_name) == func.lower(district_name)).first()
    if not district:
        district = District(district_name=district_name)
        session.add(district)
        session.commit()
    return district

def get_district_id(district_name):
    session = next(get_session())
    stmt = select(District.id).where(func.lower(District.district_name) == func.lower(district_name))
    district_id = session.execute(stmt).first()
    if not district_id:
        from db import find_similar_district
        possible_cities = find_similar_district(district_name)
        if len(possible_cities) > 0:
            return False, possible_cities
        else:
            return False, None
    else:
        return True, district_id.id
