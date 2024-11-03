from sqlalchemy import Column, Date, ForeignKey, Integer, create_engine
from sqlalchemy.orm import relationship, aliased

from db.session import get_session, Base
from models.hospital_model import Hospital

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, nullable=False)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"))
    last_donation = Column(Date())

    hospital = relationship("Hospital", back_populates="users")

def add_user_to_db(user: User):
    """
    Записывает пользователя в базу данных.
    :param user: Словарь данных о пользователе
    """
    session = next(get_session())
    new_user = User(
        telegram_id=user.telegram_id,
        hospital_id=user.hospital_id,
        last_donation=None
    )
    session.add(new_user)
    session.commit()

def update_user_data(telegram_id, new_hospital_id=None, new_last_donation=None):
    """
    Обновляет данные пользователя в таблице users по его telegram_id.
    
    :param telegram_id: ID пользователя Telegram для поиска в базе данных.
    :param new_hospital_id: Новый ID больницы (опционально).
    :param new_last_donation: Новая дата последнего визита (опционально).
    """
    session = next(get_session())
    # Находим пользователя по его telegram_id
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    
    if user:
        # Обновляем hospital_id, если передано новое значение
        if new_hospital_id is not None:
            user.hospital_id = new_hospital_id
        
        # Обновляем last_visit, если передана новая дата
        if new_last_donation is not None:
            user.last_donation = new_last_donation
        
        # Сохраняем изменения
        session.commit()
        return("Данные успешно обновлены!")
    else:
        return(f"Пользователь не найден")
    
def get_hospital_link(tg_id):
    session = next(get_session())
    result = (
        session.query(Hospital.url_address)
        .join(User, User.hospital_id == Hospital.id)
        .filter(User.telegram_id == tg_id)
        .first()
    )
    return result[0] if result else None

def get_hospital_data(tg_id):
    session = next(get_session())
    result = (
        session.query(Hospital.name, Hospital.address)
        .join(User, User.hospital_id == Hospital.id)
        .filter(User.telegram_id == tg_id)
        .first()
    )
    if result:
        result_dict = {
            "name": result.name,
            "address": result.address
                       }
        return result_dict

if __name__ == "__main__":
    get_hospital_data(902215935)