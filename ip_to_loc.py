import requests
import re
import geoip2.database

def find_location_by_ip() :
    req = requests.get("http://ipconfig.kr")
    my_ip = re.search(r'IP Address : (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', req.text)[1]

    reader = geoip2.database.Reader('GeoLite2-City_20221101\GeoLite2-City.mmdb')
    response = reader.city(my_ip)
    return response.city.name
    
print(find_location_by_ip())


