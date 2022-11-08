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
    
print(find_location_by_ip())

def now_weather() :
    city = find_location_by_ip() #도시
    apiKey = "e6612a5b5a56a202d6c75b91fd7a7a22"
    lang = 'kr' #언어
    units = 'metric' #화씨 온도를 섭씨 온도로 변경
    api = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={apiKey}&lang={lang}&units={units}"

    result = requests.get(api)
    result = json.loads(result.text)

    temperature = result['main']['temp']
    humidity = result['main']['humidity']

    return temperature, humidity

def now_location() :
    city = find_location_by_ip() #도시
    apiKey = "e6612a5b5a56a202d6c75b91fd7a7a22"
    lang = 'kr' #언어
    units = 'metric' #화씨 온도를 섭씨 온도로 변경
    api = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={apiKey}&lang={lang}&units={units}"

    result = requests.get(api)
    result = json.loads(result.text)

    lon = result['coord']['lon']
    lat = result['coord']['lat']

    return lon, lat