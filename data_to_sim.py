from pyevsim import BehaviorModelExecutor, SystemSimulator, Infinite
import datetime

if __name__ == '__main__':
	if __package__ is None:
		import sys
		from os import path
		print(path.dirname( path.dirname( path.abspath(__file__) ) ))
		sys.path.append(path.dirname( path.dirname( path.abspath(__file__) ) ))
		import loc_to_data
	else:
		from . import loc_to_data


class weather_model(BehaviorModelExecutor):
    def __init__(self, instance_time, destruct_time, name, engine_name):
        BehaviorModelExecutor.__init__(self, instance_time, destruct_time, name, engine_name)
        self.init_state("Wait")
        self.insert_state("Wait", Infinite)
        self.insert_state("Generate", 1)

        self.insert_input_port("start")

    def ext_trans(self,port, msg):
        if port == "start":
            print(loc_to_data.find_location_by_ip())
            print("Please input generate interval (second)")
            gen_time = int(input())
            self.set_gen_time(gen_time)
            print(f"Simulation Start")
            now = datetime.datetime.now()
            print(f"{now.strftime('%Y-%m-%d %H:%M:%S')} : {loc_to_data.now_weather()[0]}°C, {loc_to_data.now_weather()[1]}%, DI : {loc_to_data.now_weather()[2]}")
            self._cur_state = "Generate"

    def output(self):
        now = datetime.datetime.now()
        print(f"{now.strftime('%Y-%m-%d %H:%M:%S')} : {loc_to_data.now_weather()[0]}°C, {loc_to_data.now_weather()[1]}%, DI : {loc_to_data.now_weather()[2]}")
        return None
        
    def int_trans(self):
        if self._cur_state == "Generate":
            self._cur_state = "Generate"

    def set_gen_time(self, gen_time):
        self.update_state("Generate", gen_time)



ss = SystemSimulator()

ss.register_engine("first", "REAL_TIME", 1)
ss.get_engine("first").insert_input_port("start")
gen = weather_model(0, Infinite, "Gen", "first")
ss.get_engine("first").register_entity(gen)
ss.get_engine("first").coupling_relation(None, "start", gen, "start")
ss.get_engine("first").insert_external_event("start", None)
ss.get_engine("first").simulate()