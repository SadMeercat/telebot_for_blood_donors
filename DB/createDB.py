from sqlalchemy import create_engine
from db import parser
from db.fillDB import fill_in_hospital_data
from db.session import engine
from db.session import Base

def create_database():
    Base.metadata.create_all(bind=engine)
    hospitals = parser.get_hospitals_data()
    fill_in_hospital_data(hospitals)