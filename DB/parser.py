import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

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
            
            tmp_soup = BeautifulSoup(tmp_response.text, "html.parser")
            elements = tmp_soup.find_all('div', class_="spk-box__elem-head-item")

            for element in elements:
                tmp_link = element.find('a')

                if tmp_link:
                    text = tmp_link.get_text(strip=True)
                else:
                    text = element.get_text(strip=True)
                
                if "Регион" in text:
                    tmp_hospital["region"] = text.split(":")[1].strip()
                elif "Район" in text:
                    tmp_hospital["district"] = text.split(":")[1].strip()
                elif "Город":
                    tmp_hospital["city"] = text.split(":")[1].strip()
            
            content_items = tmp_soup.find_all('div', class_='spk-box__elem-content-item')
            for content_item in content_items:
                content_text = content_item.get_text(strip=True)
                if "Адрес" in content_text:
                    tmp_hospital["address"] = content_text.split(":")[1].strip()
                    break
            hospitals.append(tmp_hospital)
    return hospitals