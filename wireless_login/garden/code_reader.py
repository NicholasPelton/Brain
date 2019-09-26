import datetime
import time
import math

def read_code(code, sensor_data):
    d_ratio = None
    s_ratio = None
    t_ratio = None
    
    for key in sorted(code):
        print(key, code[key]['type'])
        if 'number' in code[key].keys(): new_n = code[key]['number']
        else: new_n = 0
        if 'adjust' in code[key].keys():
            if code[key]['adjust']['type'] == 'date': ratio = d_ratio # If another trigger effects this one, get the ratio
            elif code[key]['adjust']['type'] == 'timer': ratio = t_ratio
            elif code[key]['adjust']['type'] == 'sensor' : ratio = s_ratio
            if ratio != None:
                new_n = adjust(code[key]['adjust'], new_n, ratio)
            else:
                if 'deactivate' in code[key]['adjust'].keys():
                    print("This should break this iteration of the loop and immediately move to the next item")
                    continue
        else:
            ratio = None
        
        if code[key]['type'] == 'off' : return False
        elif code[key]['type'] == 'on' : return True
        elif code[key]['type'] == 'sensor':
            name = code[key]['name']
            new_n = new_n + code[key]['start']
            if sensor_check(code[key], sensor_data):
                print(sensor_data[name]['measurement'], new_n)
                if 'above' in code[key].keys():
                    if sensor_data[name]['measurement'] > new_n:
                        if code[key]['above'] == None:
                            print("None from", key, code[key])
                            s_ratio = sensor_data[name]['measurement'] / new_n
                            if s_ratio > 1: s_ratio = 1/s_ratio
                        else: return code[key]['above']
                elif 'below' in code[key].keys():
                    if sensor_data[name]['measurement'] < new_n:
                        if code[key]['below'] == None:
                            print("None from", key, code[key])
                            s_ratio = sensor_data[name]['measurement'] / new_n
                            if s_ratio > 1: s_ratio = 1/s_ratio
                        else: return code[key]['below']
                else:
                    s_ratio = None
            else:
                print("NO DATA")
                if 'no_data' in code[key].keys():
                    if code[key]['no_data'] == None:
                        s_ratio = None
                    else: return code[key]['no_data']
                    
        elif code[key]['type'] == 'timer':
            start = time_to_min(code[key]['start'])
            stop = time_to_min(code[key]['stop'])
            now = time_to_min(datetime.datetime.now().time())
            if ratio != None:
                print("adjust time!", new_n)
                start = round(start - new_n/2)
                print (start)
                stop = round(stop + new_n/2)
                print (stop)
                print (datetime.datetime.now().time())
                if start < 0: start = 1440 + start
                if stop < 0: stop = 1440 + stop
                if start >= 1440: start = start % 1440
                if stop >= 1440: stop = stop % 1440
                print(start, stop)
            print (min_to_time(start),min_to_time(stop))
            if start < stop:
                if now >= start and now < stop:
                    if code[key]['between'] == None:
                        print("None from", key, code[key])
                        t_ratio = now/(stop - start)
                    else:
                        return code[key]['between']
                else:
                    t_ratio = None
            else: #What if the start time is bigger than the end i.e. the light stays on through midnight
                if now < stop or now >= start:
                    if code[key]['between'] == None:
                        print("None from", key, code[key])
                        t_ratio = now/(1440 - (start - stop))
                    else:
                        return code[key]['between']
                else:
                    t_ratio = None
        elif code[key]['type'] == 'date':
            now = datetime.datetime.now().date()
            start = code[key]['start']
            stop = code[key]['stop']
            if now <= stop and now >= start:
                if code[key]['between'] == None:
                    print("None from", key, code[key])
                    d_delta1 = stop - start
                    d_delta2 = now - start
                    d_ratio = d_delta2/d_delta1
                else:
                    return code[key]['between']
            else:
                d_ratio = None
    print("Went through every type")
    return None
    
                    
def adjust(code, num, ratio):
    if 'geo' in code.keys():
        e = code['geo']
        num = num * (ratio**e)
    if 'sine' in code.keys():
        print(num, ratio)
        e = code['sine']
        ratio = (ratio * math.pi) - math.pi/2
        sine = ((math.sin(ratio) +1)/2)**e
        num = num * sine
        print(e,ratio,sine, num)
    if 'add' in code.keys():
        num = num + code['add']
    return num
            
def sensor_check(code,sensor_data):
    for key in sensor_data:
        if key == code['name']:
            return True
    return False
    
def min_to_time(minutes):
    if minutes < 0: minutes - 1440 - minutes
    hours = minutes//60
    minutes = minutes - hours*60
    if hours < 0: hours = hours*(-1)
    if hours > 23: hours = hours - 24
    time = datetime.time(hours,minutes)
    return time

def time_to_min(time):
    minutes = time.hour * 60 + time.minute
    return minutes
