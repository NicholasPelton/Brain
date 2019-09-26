# garden/models.py
from django.db import models
import datetime
from django.utils.dateparse import parse_date
from wireless import Wireless
import RPi.GPIO as GPIO
from django.conf import settings
from login.models import WirelessUser

wifi = WirelessUser.objects.get(pk=1)
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO_CODES = [29,31,33,35,37]

for gnum in GPIO_CODES:
    GPIO.setup(gnum,GPIO.OUT)
#    GPIO.output(gnum,GPIO.HIGH)

def upload_to(instance, filename):
    return 'users/%s/%s' % (settings.BOX_SERIAL, filename)

class Picture(models.Model):
    photo = models.ImageField(upload_to=upload_to)
    date = models.DateTimeField(auto_now_add=True)
    temp_high = models.IntegerField(default=0)
    temp_low = models.IntegerField(default=0)
    humidity_high = models.IntegerField(default=0)
    humidity_low = models.IntegerField(default=0)

class Garden(models.Model):
    STAGE_CHOICES = (
       ('SEEDLING', "Seedling"),
       ('VEGETATIVE', "Vegetative"),
    ) 
    
    serial = models.CharField(max_length=10, unique=True, default="default")
    name = models.CharField(max_length=20)
    stage = models.CharField(choices=STAGE_CHOICES, default='Vegetative', max_length=10)
    day_high = models.IntegerField(default=85)
    day_low = models.IntegerField(default=70)
    night_high = models.IntegerField(default=80)
    night_low = models.IntegerField(default=65)
    humidity_high = models.IntegerField(default=50)
    humidity_low = models.IntegerField(default=25)
    ph_high = models.DecimalField(max_digits=2, decimal_places=1 ,default=6.5)
    ph_low = models.DecimalField(max_digits=2, decimal_places=1, default=5.5)
    start_date = models.DateField(auto_now_add=True)
    current_temp = models.IntegerField(default=80)
    current_humidity = models.IntegerField(default=40)
    current_ph = models.DecimalField(max_digits=2, decimal_places=1, default=6)
    current_time = models.DateTimeField(auto_now_add=True)
    is_day = models.BooleanField(default=False)
    temp_high_today = models.IntegerField(default=0)
    temp_low_today = models.IntegerField(default=0)
    humidity_high_today = models.IntegerField(default=0)
    humidity_low_today = models.IntegerField(default=0)
    code = models.TextField(default = '')
    
    ssid = models.CharField(max_length=20, default='ssis')
    password = models.CharField(max_length=20, default='pass')

    def __str__(self):
        return self.name
    
    def connect_to_wireless(self):
        wifi = Wireless()
        booly = wifi.connect(ssid=self.ssid, password=self.password)
        return booly
            
        
        
class Outlet(models.Model):
    STYLE_CHOICES = (
        ('LIGHT', "Simple Timer"),
        ('UVB', "UVB Timer"),
        ('PUMP', "Water Pump"),
        ('SWITCH', 'On/Off Switch'),
        ('HEAT', "Heater"),
        ('COOL', "AC Unit or Fan"),
        ('HUM', "Humidifier"),
        ('DEHUM', 'De-Humidifier'),
    )
    gpio_number = models.IntegerField(default=0)
    style = models.CharField(choices=STYLE_CHOICES, default='SWITCH', max_length=15)
    is_on = models.BooleanField(default=False)
    number = models.IntegerField(default=0)
    garden = models.ForeignKey(Garden, on_delete=models.CASCADE)
    details = models.CharField(max_length=120)
    color = models.CharField(max_length=10)
    DEVICE_KEY = ''
    #Variables for timer
    time_on = models.TimeField(default=datetime.time(4,0))
    time_off = models.TimeField(default=datetime.time(22,0))
    #Variables for pump
    pump_duration = models.IntegerField(default=3)
    pump_number = models.IntegerField(default=8)
    pump_day = models.BooleanField(default=True)
    water_more = models.BooleanField(default=True)
    pump_data = {}
    #Variables for UVB
    uvb_start = models.IntegerField(default=6)
    uvb_end = models.IntegerField(default=2)
    uvb_start_date = models.DateField(default=datetime.date.today)
    uvb_end_date = models.DateField(default=(datetime.date.today()+datetime.timedelta(days=90)))
    #The special code from online
    code = models.TextField(default='')

    def time_string(self, time):
        new_time = time.strftime("%H:%M")
        return new_time
    
    def assign(self):
        self.DEVICE_KEY = self.garden.serial
        if self.number == 1:
            self. color = "blue_o"
            self.gpio_number = 37
        elif self.number == 2:
            self.gpio_number = 35
            self. color = "green_o"
        elif self.number == 3:
            self.gpio_number = 29
            self. color = "purple_o"
        elif self.number == 4:
            self.gpio_number = 33
            self. color = "red_o"
        elif self.number == 5:
            self.gpio_number = 21
            self. color = "led_o"
            self.STYLE_CHOICES = (
                ('LED', "LED Timer"),
                ('SWITCH', "LED Switch"),
            ) 
        
        
    def toggle(self):
        if self.is_on: self.off()
        else: self.on()
    
    def on(self):
        GPIO.output(self.gpio_number,GPIO.LOW)
        self.is_on = True
        self.save() 
    
    def off(self):
        GPIO.output(self.gpio_number,GPIO.HIGH)
        self.is_on = False
        self.save()
    
    def __str__(self):
        if self.number == 5: return "LED"
        else: return "Outlet " + str(self.number)
    
    def pump_calculator(self, dry_add=0):
        led = Outlet.objects.get(number=5)
        if self.pump_day:
            start = time_to_min(led.time_on)
            finish = time_to_min(led.time_off)
            if led.time_on < led.time_off:
                duration = finish - start
            else:
                duration = 1400-(start - finish)
        else:
            duration = 1400
            start = 0
        
        between = duration/(int(self.pump_number) + 1)
        self.pump_data.clear()

        for xx in range(int(self.pump_number)):
            x = xx+1
            momenton = min_to_time(round(between*x)+start)
            momentoff = min_to_time(round(between*x) + int(self.pump_duration)+start+dry_add)
            self.pump_data[x] = {"on" : momenton,"off" : momentoff}
        return dict(self.pump_data)

    def noon_calculator(self):
        if isinstance(self.time_on,str):
            self.time_on = datetime.datetime.strptime(time_on,"%H:%M").time()
        if isinstance(self.time_off,str):
            self.time_on = datetime.datetime.strptime(time_off,"%H:%M").time()
        time_min = round(time_to_min(self.time_on)/2 + time_to_min(self.time_off)/2)
        if self.time_on > self.time_off:
            if time_min >=720: time_min = time_min - 720
            else: time_min = time_min + 720
        time = min_to_time(time_min)
        print("camera will go off at ",time)
        return time

    def uvb_calculator(self):
        if isinstance(self.uvb_start_date,str):self.uvb_start_date = parse_date(self.uvb_start_date)
        if isinstance(self.uvb_end_date,str):self.uvb_end_date = parse_date(self.uvb_end_date)       
        
        if self.uvb_start_date > self.uvb_end_date:
            self.uvb_end_date, self.uvb_start_date = self.uvb_start_date, self.uvb_end_date
        if datetime.date.today() <= self.uvb_start_date:
            duration = self.uvb_start*60
        elif datetime.date.today() >= self.uvb_end_date:
            duration = self.uvb_end*60
        else:
            day_total = (self.uvb_end_date - self.uvb_start_date).days
            day_count = (datetime.date.today() - self.uvb_start_date).days
            ratio = day_count/day_total
            duration = round((int(self.uvb_start) * (1-ratio) + int(self.uvb_end) * ratio) * 60)
            
        led = Outlet.objects.get(number=5, garden=self.garden)
        if led.time_on < led.time_off:
            led_duration = time_to_min(led.time_off) - time_to_min(led.time_on)
        else:
            led_duration = 1400-(time_to_min(led.time_on) - time_to_min(led.time_off))
        
        uvb_start_time = min_to_time(time_to_min(led.time_on) + round((led_duration - duration)/2))
        uvb_end_time = min_to_time(time_to_min(uvb_start_time) + duration)
        return uvb_start_time, uvb_end_time

def min_to_time(minutes):
    hours = minutes//60
    minutes = minutes - hours*60
    if hours < 0: hours = hours*(-1)
    if hours > 23: hours = hours - 24
    time = datetime.time(hours,minutes)
    return time

def time_to_min(time):
    minutes = time.hour * 60 + time.minute
    return minutes
