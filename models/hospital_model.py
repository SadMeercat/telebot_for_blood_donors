from sqlalchemy import Column, ForeignKey, Integer, String, func, select
from sqlalchemy.orm import relationship
from db.session import get_session, Base

class Hospital(Base):
    __tablename__ = "hospitals"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    city_id = Column(Integer, ForeignKey("cities.id"))
    district_id = Column(Integer, ForeignKey("districts.id"))
    address = Column(String(100))
    url_address = Column(String(100))

    users = relationship("User", back_populates="hospital")
    city = relationship("City", back_populates="hospitals")
    district = relationship("District", back_populates="hospitals")

def add_hospital(name, region_id, city_id, district_id, address, url_address):
    session = next(get_session())
    
    # Проверяем, существует ли уже такая больница
    existing_hospital = session.query(Hospital).filter(
        func.lower(Hospital.name) == name.lower(),
        Hospital.city_id == city_id,
        Hospital.district_id == district_id,
        func.lower(Hospital.address) == address.lower()
    ).first()
    
    if not existing_hospital:
        # Создаем новую запись больницы
        hospital = Hospital(
            name=name,
            city_id=city_id,
            district_id=district_id,
            address=address,
            url_address=url_address
        )
        session.add(hospital)
        session.commit()

def get_hospital_id(city_id, district_id, name=None):
    session = next(get_session())
    if not name:
        stmt = select(Hospital.id, Hospital.name).where(Hospital.city_id == city_id, 
                                                        Hospital.district_id == district_id)
        hospitals = session.execute(stmt).all()
    else:
        stmt = select(Hospital.id).where(Hospital.city_id == city_id, 
                                         Hospital.district_id == district_id,
                                         Hospital.name == name)
        hospitals = session.execute(stmt).first()
    return hospitals
