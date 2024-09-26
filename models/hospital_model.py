from sqlalchemy import Column, ForeignKey, Integer, String, func, select
from sqlalchemy.orm import relationship
from DB.session import get_session, Base

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
    region = relationship("Region", back_populates="hospital")
    city = relationship("City", back_populates="hospital")
    district = relationship("District", back_populates="hospital")

def add_hospital(name, region_id, city_id, district_id, address, url_address):
    session = next(get_session())
    
    # Проверяем, существует ли уже такая больница
    existing_hospital = session.query(Hospital).filter(
        func.lower(Hospital.name) == name.lower(),
        Hospital.region_id == region_id,
        Hospital.city_id == city_id,
        Hospital.district_id == district_id,
        func.lower(Hospital.address) == address.lower()
    ).first()
    
    if not existing_hospital:
        # Создаем новую запись больницы
        hospital = Hospital(
            name=name,
            region_id=region_id,
            city_id=city_id,
            district_id=district_id,
            address=address,
            url_address=url_address
        )
        session.add(hospital)
        session.commit()

# # Функция для получения существующих регионов
# def get_existing_regions():
#     session = next(get_session())
#     regions = session.query(Hospital.region).distinct().all()  # Получаем уникальные регионы
#     return [region[0] for region in regions]  # Возвращаем список регионов

# # Функция для проверки существования больницы с подсказками
# def hospital_exists_by_region(region_name):
#     session = next(get_session())
#     # Приводим region_name к нижнему регистру и создаем запрос
#     exists_stmt = session.query(
#         select([func.count()]).where(func.lower(Hospital.region) == region_name.lower())
#     )
    
#     # Выполняем запрос и получаем результат
#     result = session.execute(exists_stmt).scalar()  # Получаем количество записей

#     if result > 0:
#         return True, None  # Если запись найдена, возвращаем True без подсказки
    
#     # Если запись не найдена, ищем возможные варианты
#     existing_regions = get_existing_regions()
#     suggestions = [region for region in existing_regions if region.lower().startswith(region_name.lower())]
#     return False, suggestions  # Возвращаем False и возможные варианты