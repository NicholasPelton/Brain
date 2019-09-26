# login/models
import subprocess
from django.db import models
from wireless import Wireless
import os
from time import sleep
import http.client as httplib

class WirelessUser(models.Model):
    wifi = Wireless()
    name = models.CharField(max_length=50, default="Home")
    ssid = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    is_on = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

    def start_wifi_check(self):
        self.is_on=self.have_internet()
        return self.is_on
    
    def connectus(self):
        self.is_on = self.wifi.connect(ssid=self.ssid,password=self.password)
        print("First try...")
        if self.is_on == False:
            print("Second try...")
            self.is_on = self.wifi.connect(ssid=self.ssid,password=self.password)
        if self.is_on == True:
            print (self.ssid,self.password)
            print("run worker")
            #sleep(2)
            os.system('sudo supervisorctl start motherworker')
        self.save()
        return self.is_on
    
    def wifi_check(self):
        #print (self.wifi.current())
        #if self.wifi.current() == None:
        if self.have_internet() != True:
            if self.is_on == True:
                os.system('sudo supervisorctl stop motherworker')
                self.is_on = False
        else:
            if self.is_on == False:
                self.is_on = True
                os.system('sudo supervisorctl start motherworker')
        self.save()
        return self.is_on

    def have_internet(self):
        conn = httplib.HTTPConnection('www.google.com', timeout=5)
        try:
            conn.request("HEAD", "/")
            conn.close()
            print ("We have true internet")
            return True
        except:
            conn.close()
            print ("No internet connection!")
            return False

    def refresh_worker(self):
        os.system('sudo supervisorctl stop motherworker')
        os.system('sudo supervisorctl start motherworker')
        print("worker has been restarted!")

# Create your models here.
