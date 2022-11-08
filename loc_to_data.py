import requests
import json
import re
import geoip2.database

def find_location_by_ip() :
    req = requests.get("http://ipconfig.kr")
    my_ip = re.search(r'IP Address : (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', req.text)[1]

    reader = geoip2.database.Reader('GeoLite2-City_20221101\GeoLite2-City.mmdb')
    response = reader.city(my_ip)
    return response.city.name

def now_weather() :
    with open('apikey.json', 'r') as f :
        api_data = json.load(f)

    city = find_location_by_ip() #도시
    apiKey = api_data["apikey"]
    lang = 'kr' #언어
    units = 'metric' #화씨 온도를 섭씨 온도로 변경
    api = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={apiKey}&lang={lang}&units={units}"

    result = requests.get(api)
    result = json.loads(result.text)

    temperature = result['main']['temp']
    humidity = result['main']['humidity']
    di = (1.8 * temperature) - 0.55 * (1 - (0.01 * humidity)) * (1.8 * temperature - 26) + 32

    return temperature, humidity, di
