from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker
from prepDB.schemas import Hospital

engine = create_engine("sqlite:///data.db")
Session = sessionmaker(bind=engine)
session = Session()

def add_hospitals_to_db(hospitals):
    """
    Записывает список больниц в базу данных.
    :param hospitals: Список словарей с данными о больницах
    """
    for hospital in hospitals:
        new_hospital = Hospital(
            name=hospital['name'],
            region=hospital.get('region'),
            district=hospital.get('district'),
            city=hospital.get('city'),
            address=hospital['address'],
            url_address=hospital['url_address']
        )
        session.add(new_hospital)
    
    # Сохраняем изменения в базе данных
    session.commit()

def update_hospitals_from_site(new_hospitals):
    """
    Перепроверяет данные с сайта и обновляет базу данных.
    :param new_hospitals: Список словарей с новыми данными о больницах
    """
    for hospital in new_hospitals:
        # Проверяем, есть ли такая больница в базе данных (по имени и адресу)
        existing_hospital = session.query(Hospital).filter_by(
            name=hospital['name'], address=hospital['address']
        ).first()
        
        if existing_hospital is None:
            # Если больница не найдена, добавляем ее в базу данных
            new_hospital = Hospital(
                name=hospital['name'],
                region=hospital.get('region'),
                district=hospital.get('district'),
                city=hospital.get('city'),
                address=hospital['address']
            )
            session.add(new_hospital)
    
    # Сохраняем изменения в базе данных
    session.commit()

# Функция для получения существующих регионов
def get_existing_regions():
    regions = session.query(Hospital.region).distinct().all()  # Получаем уникальные регионы
    return [region[0] for region in regions]  # Возвращаем список регионов

# Функция для проверки существования больницы с подсказками
def hospital_exists_by_region(region_name):
    # Приводим region_name к нижнему регистру и создаем запрос
    exists_stmt = session.query(
        select([func.count()]).where(func.lower(Hospital.region) == region_name.lower())
    )
    
    # Выполняем запрос и получаем результат
    result = session.execute(exists_stmt).scalar()  # Получаем количество записей

    if result > 0:
        return True, None  # Если запись найдена, возвращаем True без подсказки
    
    # Если запись не найдена, ищем возможные варианты
    existing_regions = get_existing_regions()
    suggestions = [region for region in existing_regions if region.lower().startswith(region_name.lower())]
    return False, suggestions  # Возвращаем False и возможные варианты