from sqlalchemy import create_engine
from DB import parser
from DB.session import engine
import os
from sqlalchemy.ext.declarative import declarative_base

from models import Region, City, District, Hospital
from models.city_model import get_or_create_city
from models.district_model import get_or_create_district
from models.hospital_model import add_hospital
from models.region_model import get_or_create_region
from DB.session import Base

def createDB():
    Base.metadata.create_all(bind=engine)
    fill_in_hospital_data()

def fill_in_hospital_data():
    hospitals = parser.get_hospitals_data()
    for hospital in hospitals:
        region = get_or_create_region(hospital['region']).id
        city = get_or_create_city(hospital['city']).id
        district = get_or_create_district(hospital['district']).id

        add_hospital(
            name=hospital['name'],
            region_id=region,
            city_id=city,
            district_id=district,
            address=hospital['address'],
            url_address=hospital['url_address']
        )
if __name__ == "__main__":
    createDB()