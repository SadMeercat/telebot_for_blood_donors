from db import parser
from models.hospital_model import add_hospital
from models.region_model import get_or_create_region
from models.city_model import get_or_create_city
from models.district_model import get_or_create_district


def fill_in_hospital_data(hospitals):
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