import re
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from dotenv import load_dotenv
import os

load_dotenv()

def get_hospitals_data() -> list:
    url = "https://yadonor.ru/donorstvo/gde-sdat/where/"
    home_url = "https://yadonor.ru"

    ua = UserAgent()

    headers = {
        "User-Agent": ua.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://yadonor.ru/",
        "Cookie": "feedbackform=dsdfsf; cookieModal=1; PHPSESSID=hctnhfiqpf5bmf1unm3s56uk20; domen_name=yadonor.ru; ajax_name=yadonor.ru; ds_lk=https%3A%2F%2Fyadonor.ru%2Fperson%2F; ds_name=donorsapiens.yadonor.ru; session-cookie=17f8435fb314f8973157f2bc1e808458284e1ce1545aff6c01195308be102ce961dfb2aedd62cd8cf7f9a020b4be8970; _ym_uid=1727204536374038373; _ym_d=1727204536; _ym_isad=2; cRegion=0; special_v=no"
    }

    session = requests.Session()

    response = session.get(url=url, headers=headers)

    if response.status_code != 200:
        print(f"Не удалось подключиться:{response.status_code}")
        return
    soup = BeautifulSoup(response.text, "html.parser")

    div_block = soup.find('div', class_="maps-content__spoler js-maps-spoler-box")
    if div_block:
        links = div_block.find_all('a')
        hospitals = []

        for link in tqdm(links, desc="Прасинг ссылок", ncols=100):
            tmp_hospital = {}
            tmp_hospital["name"] = link.get_text()
            tmp_hospital["url_address"] = home_url + link.get("href")
            tmp_response = session.get(url=tmp_hospital["url_address"], headers=headers)
            print(tmp_hospital["url_address"])
            tmp_soup = BeautifulSoup(tmp_response.text, "html.parser")
            elements = tmp_soup.find_all('div', class_="spk-box__elem-head-item")

            for element in elements:
                tmp_link = element.find('a')

                if tmp_link:
                    text = tmp_link.get_text(strip=True)
                else:
                    text = element.get_text(strip=True)
            
                if "Город":
                    tmp_hospital["city"] = text.split(":")[1].strip()
            
            content_items = tmp_soup.find_all('div', class_='spk-box__elem-content-item')
            for content_item in content_items:
                content_text = content_item.get_text(strip=True)
                if "Адрес" in content_text:
                    tmp_hospital["address"] = content_text.split(":")[1].strip()
                    
                    tmp_hospital["district"] = get_district(tmp_hospital["address"])
                    break
            hospitals.append(tmp_hospital)
    return hospitals

def get_district(address: str):
    api_key = os.getenv('YANDEX_TOKEN')

    abbreviations = {
        "Ю.":"Юных"
    }

    for key in abbreviations.keys():
        if key in address:
            address = address.replace(key, abbreviations[key])

    headers = {
     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }
    url = f"https://geocode-maps.yandex.ru/1.x/?apikey={api_key}&geocode={address}&format=json"

    response = requests.get(url, headers=headers)
    data = response.json()

    print(url)

    # Извлечение района из ответа
    components = data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["metaDataProperty"]["GeocoderMetaData"]["Address"]["Components"]

    district = next(
        (item["name"] for item in components if item["kind"] == "area" and "район" in item["name"].lower()), 
        None
    )

    if district:
        district = district.replace("район", "")

    return district

def get_lights(url: str) -> dict: 
    ua = UserAgent()
    headers = {
        "User-Agent": ua.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://yadonor.ru/",
        "Cookie": "feedbackform=dsdfsf; cookieModal=1; PHPSESSID=hctnhfiqpf5bmf1unm3s56uk20; domen_name=yadonor.ru; ajax_name=yadonor.ru; ds_lk=https%3A%2F%2Fyadonor.ru%2Fperson%2F; ds_name=donorsapiens.yadonor.ru; session-cookie=17f8435fb314f8973157f2bc1e808458284e1ce1545aff6c01195308be102ce961dfb2aedd62cd8cf7f9a020b4be8970; _ym_uid=1727204536374038373; _ym_d=1727204536; _ym_isad=2; cRegion=0; special_v=no"
    }

    session = requests.Session()
    response = session.get(url=url, headers=headers)

    if response.status_code != 200:
        print("Не удалось подключиться")
    else:
        soup = BeautifulSoup(response.text, "html.parser")
        lights_div = soup.find('div', class_="spk-lights")
        all_lights = {}

        if lights_div:
            lights = lights_div.find_all('div', class_="spk-lights__item")
            for light in lights:
                blood_group = ' '.join(light.find('div', class_="spk-lights__head").get_text().strip().split())
            
                greens = light.find_all('div', class_="spk-lights__group-item spk-lights__group-item--max")
                yellows = light.find_all('div', class_="spk-lights__group-item spk-lights__group-item--middle")
                reds = light.find_all('div', class_="spk-lights__group-item spk-lights__group-item--min")
                whites = light.find_all('div', class_="spk-lights__group-item spk-lights__group-item--not")
                grays = light.find_all('div', class_="spk-lights__group-item spk-lights__group-item--gray")

                rh_s = {}

                if greens:
                    for green in greens:
                        rh_s[' '.join(green.get_text().strip().split())] = '🟢'
                if yellows:
                    for yellow in yellows:
                        rh_s[' '.join(yellow.get_text().strip().split())] = '🟡'
                if reds:
                    for red in reds:
                        rh_s[' '.join(red.get_text().strip().split())] = '🔴'
                if whites:
                    for white in whites:
                        rh_s[' '.join(white.get_text().strip().split())] = '⚪️'
                if grays:
                    for gray in grays:
                        rh_s[' '.join(gray.get_text().strip().split())] = '❌'
                all_lights[blood_group] = rh_s
    return all_lights

if __name__ == "__main__":
    get_hospitals_data()