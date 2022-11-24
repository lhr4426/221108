from pyevsim import SystemSimulator, BehaviorModelExecutor, SysMessage
from pyevsim.definition import *
import datetime
import requests
import json
import re
import geoip2.database

def get_weather() :
        req = requests.get("http://ipconfig.kr")
        my_ip = re.search(r'IP Address : (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', req.text)[1]

        reader = geoip2.database.Reader('GeoLite2-City_20221101/GeoLite2-City.mmdb')
        response = reader.city(my_ip)

        with open('apikey.json', 'r') as f :
            api_data = json.load(f)

        city = response.city.name #도시
        apiKey = api_data["apikey"]
        lang = 'kr' #언어
        units = 'metric' #화씨 온도를 섭씨 온도로 변경
        api = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={apiKey}&lang={lang}&units={units}"

        result = requests.get(api)
        result = json.loads(result.text)

        temperature = result['main']['temp']
        humidity = result['main']['humidity']
        di = (1.8 * temperature) - 0.55 * (1 - (0.01 * humidity)) * (1.8 * temperature - 26) + 32

        return response.city.name, temperature, humidity, di

class take_weather(BehaviorModelExecutor):
    def __init__(self, instance_time, destruct_time, name, engine_name):
        BehaviorModelExecutor.__init__(self, instance_time, destruct_time, name, engine_name)
        self.init_state("Wait")
        self.insert_state("Wait", Infinite)
        self.insert_state("Weather", 1)

        self.insert_input_port("start")
        self.insert_output_port("Very_High_DI")
        self.insert_output_port("High_DI")

        self.first_time = False
        self.gen_time = 0

    def ext_trans(self,port, msg):
        if port == "start":
            print("Please input generate interval (second)")
            gen_time = int(input())
            self.set_gen_time(gen_time)
            self.first_time = True
            self._cur_state = "Weather"

    def output(self) :
        if self.first_time == True :
            self.update_state("Weather", self.gen_time)
            self.first_time = False
        now = datetime.datetime.now()
        now_weather = list(get_weather())
        now_weather[3] = 79
        print(f"{now.strftime('%Y-%m-%d %H:%M:%S')} | City : {now_weather[0]} | Temperature : {now_weather[1]}°C | Humidity : {now_weather[2]}% | DI : {now_weather[3]}")

        if now_weather[3] >= 80 :
            msg = SysMessage(self.get_name(), "Very_High_DI")
            return msg 
        elif now_weather[3] >= 75 :
            msg = SysMessage(self.get_name(), "High_DI")
            return msg


    def int_trans(self):
        if self._cur_state == "Weather":
            self._cur_state = "Weather"

    def set_gen_time(self, gen_time):
        self.gen_time = gen_time


class VeryHighHandler (BehaviorModelExecutor):
    def __init__(self, instance_time, destruct_time, name, engine_name):
        BehaviorModelExecutor.__init__(self, instance_time, destruct_time, name, engine_name)

        self.init_state("wait")
        self.insert_state("wait", Infinite)
        self.insert_state("warning", 1)

        self.insert_input_port("Very_High_DI")
    
    def ext_trans(self, port, msg) :
        if port == "Very_High_DI" :
            self._cur_state = "warning"
            
    def output(self):
        print("Warning! Very High Discomfort Index!")
        return None

    def int_trans(self) :
        if self._cur_state == "warning" :
            self._cur_state = "wait"

class HighHandler (BehaviorModelExecutor):
    def __init__(self, instance_time, destruct_time, name, engine_name):
        BehaviorModelExecutor.__init__(self, instance_time, destruct_time, name, engine_name)

        self.init_state("wait")
        self.insert_state("wait", Infinite)
        self.insert_state("caution", 1)

        self.insert_input_port("High_DI")
    
    def ext_trans(self, port, msg) :
        if port == "High_DI" :
            self._cur_state = "caution"
            
    def output(self):
        print("Caution. High Discomfort Index.")
        return None

    def int_trans(self) :
        if self._cur_state == "caution" :
            self._cur_state = "wait"
    
ss = SystemSimulator()
weather_engine = ss.register_engine("weather_engine", "REAL_TIME", 1)
weather_engine.insert_input_port("start")

md_take_weather = take_weather(0, Infinite, "take_weather", "weather_engine")
md_VeryHighHandler = VeryHighHandler(0, Infinite, "VeryHighHandler", "weather_engine")
md_HighHandler = HighHandler(0, Infinite, "HighHandler", "weather_engine")


weather_engine.register_entity(md_take_weather)
weather_engine.register_entity(md_VeryHighHandler)
weather_engine.register_entity(md_HighHandler)

weather_engine.coupling_relation(None, weather_engine.start, md_take_weather, md_take_weather.start)
weather_engine.coupling_relation(md_take_weather, md_take_weather.Very_High_DI, md_VeryHighHandler, md_VeryHighHandler.Very_High_DI)
weather_engine.coupling_relation(md_take_weather, md_take_weather.High_DI, md_HighHandler, md_HighHandler.High_DI)

weather_engine.insert_external_event(weather_engine.start, None)
weather_engine.simulate()