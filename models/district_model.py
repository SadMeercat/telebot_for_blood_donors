from sqlalchemy import Column, Integer, String, func
from sqlalchemy.orm import relationship

from DB.session import get_session, Base

class District(Base):
    __tablename__ = "districts"
    id = Column(Integer, primary_key=True)
    district_name = Column(String(100), nullable=False)

    hospital = relationship("Hospital", back_populates="district")

def get_or_create_district(district_name:str):
    session = next(get_session())
    district = session.query(District).filter(func.lower(District.district_name) == func.lower(district_name)).first()
    if not district:
        district = District(district_name=district_name)
        session.add(district)
        session.commit()
    return district