from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os

load_dotenv()
# Подключение к базе данных
engine = create_engine(os.getenv('DATABASE_URL'))

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)

# Создаем базовый класс для всех моделей
Base = declarative_base()

# Функция для получения сессии
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()