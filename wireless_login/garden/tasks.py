from garden.models import Garden, Outlet
import usbtemper
from picamera import PiCamera
import time
import datetime
from garden.models import Picture
from django.core.files import File
from garden.consumers import change_detect
from login.models import WirelessUser
from . import code_reader
import json

# refresh worker every hour just incase something stupid happens
#def refresh_worker():
#    wifiguy = WirelessUser.objects.get(pk=1)
#    wifiguy.refresh_worker()

# Create your tests here.
def start_up():
    update_check()

def update_check():

    # check to see if we have wifi, and refresh worker if need be
    wifiguy = WirelessUser.objects.get(pk=1)

    # Get the garden and find the stats
    garden = Garden.objects.get(pk=3)
    garden.current_temp = usbtemper.findtemp()
    garden.current_humidity = usbtemper.findhum()

    # Double check highs and lows for data
    
    garden.current_temp =int(garden.current_temp)
    garden.current_humidity = int(garden.current_humidity)
    if garden.current_temp > garden.temp_high_today: 
        garden.temp_high_today = garden.current_temp
    if garden.current_temp < garden.temp_low_today or garden.temp_low_today == 0: 
        garden.temp_low_today = garden.current_temp
    if garden.current_humidity > garden.humidity_high_today: 
        garden.humidity_high_today = garden.current_humidity
    if garden.current_humidity < garden.humidity_low_today or garden.humidity_low_today == 0: 
        garden.humidity_low_today = garden.current_humidity
    
    garden.save()
    
    print ('-----------------------THIS IS AN UPDATE-----------------------')
    print(garden.current_temp)
    print(garden.current_humidity)
    #Here comes each potential outlet.
    for x in range (1,6):
        outlet_check(x)

    wifiguy.wifi_check()
        
def camera_check(now=None):
    if now == None: path = datetime.datetime.now().strftime("%m-%d-%Y-%M")+'.png'
    else: path = "current.png"
    garden = Garden.objects.get(pk=3)
    with PiCamera() as cam:
        picture = Picture()
        cam.start_preview()
        time.sleep(2)
        cam.capture('/home/honky/wireless_login/mostrecent.jpeg')
        p = open('/home/honky/wireless_login/mostrecent.jpeg', 'rb')
        django_file = File(p)
        picture.photo.save(path, django_file, save=True)
        cam.stop_preview()
        picture.temp_high = garden.temp_high_today
        picture.temp_low = garden.temp_low_today
        picture.humidity_high = garden.humidity_high_today
        picture.humidity_low = garden.humidity_low_today
        picture.save()
        p.close()

def new_day():
    garden = Garden.objects.get(pk=3)
    garden.temp_high_today = garden.current_temp
    garden.temp_low_today = garden.current_temp
    garden.humidity_high_today = garden.current_humidity
    garden.humidity_low_today = garden.current_humidity
    garden.save()

def outlet_check(num):
    outlet = Outlet.objects.get(number=num)
    garden = Garden.objects.get(pk=3)
    led = Outlet.objects.get(number = 5)
    flip_original = outlet.is_on
    flip = flip_original # This will tell if the outlet is ultimately on or off
    time_now = datetime.datetime.now().time()
    if timer_check(led.time_on, led.time_off): # Day or night?
        temp_high = garden.day_high
        temp_low = garden.day_low
        print("day")
    else:
        temp_high = garden.night_high
        temp_low = garden.night_low
        print("night")

    if outlet.style=="LIGHT":
        flip = timer_check(outlet.time_on, outlet.time_off)
        if temp_high < garden.current_temp: flip = False
    elif outlet.style=="UVB":
        time_on,time_off = outlet.uvb_calculator()
        flip = timer_check(time_on,time_off)
        if garden.day_high < garden.current_temp: flip = False
    elif outlet.style=="PUMP":
        flip = False
        if garden.current_humidity<garden.humidity_low:
            dry_add=2
        else:
            dry_add=0
        pump_data=outlet.pump_calculator(dry_add)
        now = datetime.datetime.now().time()
        for xx in range(int(outlet.pump_number)):
            x = xx+1
            if now > pump_data[x]['on'] and now < pump_data[x]['off']:
                flip = True # Make flip true if the time falls within any on/off set
    elif outlet.style=="HEAT":
        if temp_low > garden.current_temp: flip = True
        if temp_high < garden.current_temp: flip = False

    elif outlet.style=="COOL":
        if temp_low > garden.current_temp: flip = False
        if temp_high < garden.current_temp: flip = True
    
    elif outlet.style=="HUM":
        if garden.humidity_low > garden.current_humidity: flip = True
        if garden.humidity_high < garden.current_humidity: flip = False
    
    elif outlet.style=="DEHUM":
        if garden.humidity_low > garden.current_humidity: flip = False
        if garden.humidity_high < garden.current_humidity: flip = True
    '''
    elif outlet.style=="ONLINE":
        code = json.loads(outlet.code)
        result = code_reader.read_code(code)
        if result == None:
            pass
        else:
            flip = result 
    '''
    if flip==True: #Flip will tell us what to do
        outlet.on()
    else:
        outlet.off()
    
    if flip != flip_original: change_detect.toggler(outlet.number,flip)
    if outlet.number == 5:
        now = datetime.datetime.now().time()
        now = now.replace(second=0, microsecond=0)
        noon = outlet.noon_calculator()
        #garden_code = json.loads(garden.code)
        #if camera_times in garden_code.keys():
        #    for key in sorted(garden_code['camera_times']):
        #        if time_now == gaden_code['camera_times'][key]:
        #            camera_check()
        print("Camera goes off at high ",noon)
        if now == noon:
            camera_check()

    print (outlet,outlet.style,outlet.is_on)
        

def timer_check(time_on,time_off):
    now = datetime.datetime.now().time()
    if time_on < time_off:
        if now > time_on and now < time_off:
            return True
        else:
            return False
    else:
        if now > time_off and now < time_on:
            return False
        else:
            return True
            
