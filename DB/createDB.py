from db.session import Base, engine
from db.fillDB import fill_in_hospital_data
from db.parser import get_hospitals_data

def create_database():
    Base.metadata.create_all(bind=engine)
    hospitals = get_hospitals_data()
    fill_in_hospital_data(hospitals)