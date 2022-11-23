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

class timer(BehaviorModelExecutor):
    def __init__(self, instance_time, destruct_time, name, engine_name):
        BehaviorModelExecutor.__init__(self, instance_time, destruct_time, name, engine_name)
        self.init_state("Wait")
        self.insert_state("Wait", Infinite)
        self.insert_state("Ringing", 1)

        self.insert_input_port("start")
        self.insert_output_port("alarm")

    def ext_trans(self,port, msg):
        if port == "start":
            print("Please input generate interval (second)")
            gen_time = int(input())
            self._cur_state = "Ringing"
            self.set_gen_time(gen_time)

    def output(self) :
        return SysMessage(self.get_name(), "alarm")
        
    def int_trans(self):
        if self._cur_state == "Ringing":
            self._cur_state = "Ringing"

    def set_gen_time(self, gen_time):
        self.update_state("Ringing", gen_time)


class take_weather (BehaviorModelExecutor):
    def __init__(self, instance_time, destruct_time, name, engine_name):
        BehaviorModelExecutor.__init__(self, instance_time, destruct_time, name, engine_name)

        self.init_state("Wait")
        self.insert_state("Wait", Infinite)
        self.insert_state("Weather", 1)

        self.insert_input_port("Ring")
        self.insert_output_port("Very_high_di")
        self.insert_output_port("High_di")


    def ext_trans(self,port, msg):
        if port == "Ring":
            self._cur_state = "Weather"

    def output(self):
        now = datetime.datetime.now()
        # now_weather = get_weather()
        now_weather = ['hey', 20, 30, 75]
        print(f"{now.strftime('%Y-%m-%d %H:%M:%S')} | City : {now_weather[0]} | Temperature : {now_weather[1]}°C | Humidity : {now_weather[2]}% | DI : {now_weather[3]}")

        if now_weather[3] >= 80 :
            msg = SysMessage(self.get_name(), "Very_high_di")
            return msg 
        elif now_weather[3] >= 75 :
            msg = SysMessage(self.get_name(), "High_di")
            return msg

   
    def int_trans(self):
        if self._cur_state == "Weather":
            self._cur_state = "Wait"

class check_di (BehaviorModelExecutor):
    def __init__(self, instance_time, destruct_time, name, engine_name):
        BehaviorModelExecutor.__init__(self, instance_time, destruct_time, name, engine_name)

        self.init_state("wait")
        self.insert_state("wait", Infinite)
        self.insert_state("v-h", 1)
        self.insert_state("h", 1)

        self.insert_input_port("very_high_di")
        self.insert_input_port("high_di")
    
    def ext_trans(self, port, msg) :
        if port == "very_high_di" :
            self._cur_state = "v-h"
        if port == "high_di" :
            self._cur_state = "h"
            
    def output(self):
        if self._cur_state == "v-h" : print("Very-High")
        if self._cur_state == "h" : print("High")
        return None

    def int_trans(self) :
        if self._cur_state == "v-h" :
            self._cur_state = "wait"
        if self._cur_state == "h" :
            self._cur_state = "wait"
    

# System Simulator Initialization
ss = SystemSimulator()
first = ss.register_engine("first", "REAL_TIME", 1)
first.insert_input_port("start")

main_timer = timer(0, Infinite, "timer", "first")
main_weather = take_weather(0, Infinite, "weather", "first")
main_check = check_di(0, Infinite, "check", "first")
# h_di = high_di(0, Infinite, "highDI", "first")

first.register_entity(main_weather)
first.register_entity(main_timer)
first.register_entity(main_check)
# first.register_entity(h_di)

first.coupling_relation(None, first.start, main_timer, main_timer.start)
first.coupling_relation(main_timer, main_timer.alarm, main_weather, main_weather.Ring)
first.coupling_relation(main_weather, main_weather.Very_high_di, main_check, main_check.very_high_di)
first.coupling_relation(main_weather, main_weather.High_di, main_check, main_check.high_di)
# first.coupling_relation(main_weather, main_weather.High_di, h_di, h_di.high_temp_in)
first.insert_external_event(first.start, None)
first.simulate()