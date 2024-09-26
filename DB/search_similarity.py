from difflib import get_close_matches

from sqlalchemy import select
from models import Region, City, District
from db import get_session

def find_similar_region(region_name: str):
    session = next(get_session())
    stmt = select(Region.region_name)
    region_names = [region[0] for region in session.execute(stmt)]
    return get_close_matches(region_name, region_names, n=3, cutoff=0.6)

def find_similar_city(city_name: str):
    session = next(get_session())
    cities = session.query(City.city_name).all()
    city_names = [city[0] for city in cities]
    return get_close_matches(city_name, city_names, n=3, cutoff=0.6)

def find_similar_district(district_name: str):
    session = next(get_session())
    districts = session.query(District.district_name).all()
    district_names = [district[0] for district in districts]
    return get_close_matches(district_name, district_names, n=3, cutoff=0.6)