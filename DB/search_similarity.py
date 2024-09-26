from difflib import get_close_matches
from sqlalchemy import select

from models.city_model import City
from models.region_model import Region
from models.district_model import District
from db.session import get_session

def find_similar_region(region_name: str):
    session = next(get_session())
    stmt = select(Region.region_name)
    region_names = [region[0] for region in session.execute(stmt)]
    return get_close_matches(region_name, region_names, n=3, cutoff=0.6)

def find_similar_city(city_name: str):
    session = next(get_session())
    stmt = select(City.city_name)
    city_names = [city[0] for city in session.execute(stmt)]
    return get_close_matches(city_name, city_names, n=3, cutoff=0.6)

def find_similar_district(district_name: str):
    session = next(get_session())
    stmt = select(District.district_name)
    district_names = [district[0] for district in session.execute(stmt)]
    return get_close_matches(district_name, district_names, n=3, cutoff=0.6)