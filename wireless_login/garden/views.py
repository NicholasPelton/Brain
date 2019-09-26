# garden/views.py
import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import OnlineCredentialForm
from .models import Garden, Outlet, time_to_min, min_to_time
from login.models import WirelessUser
from django.http import HttpResponse
import datetime
from django.conf import settings
import wireless_login.urls

# Create your views here.
        
def garden(request, username=None, garden=None):
    wireless = WirelessUser.objects.get(pk=1)
    garden = Garden.objects.get(pk=3)
    context = {'garden':garden, 'wireless':wireless}
    return render(request,'garden/garden.html', context)

def toggler(request, username=None, garden=None):
    outlet_num = request.POST.get('outlet_num')
    garden = Garden.objects.get(pk=3)
    print(garden)
    print(outlet_num)
    outlet = Outlet.objects.get(number=outlet_num,garden=garden)
    outlet.toggle()
    if outlet.is_on: text = {'button_state':"power"}
    else: text = {'button_state':"power_off"}
    return JsonResponse(text)

def outlet(request, outlet_num=None):
    wireless = WirelessUser.objects.get(pk=1)
    garden = Garden.objects.get(pk=3)
    outlet = garden.outlet_set.get(number=outlet_num)
    context = {'garden':garden, 'outlet':outlet, 'wireless':wireless}
    return render(request,'garden/outlet.html', context)
        
def outlet_template(request, outlet_num=None):
    wireless = WirelessUser.objects.get(pk=1)
    garden = Garden.objects.get(pk=3)
    outlet = garden.outlet_set.get(number=outlet_num)
    context = {'garden':garden, 'outlet':outlet, 'wireless':wireless}
    return render(request, 'garden/outlet_types/'+str(outlet.style)+'.html', context)

def variable_change(request, garden_serial=None):
    wireless = WirelessUser.objects.get(pk=1)
    if request.method == 'POST':
        print ("variable change")
        garden = Garden.objects.get(pk=3)
        #Update variable as defined in json
        if request.POST['outlet_number'] == "0":
            print("No OUTLET!")
            if request.POST['variable'] != "no_change":

                setattr(garden, request.POST['variable'], request.POST['new_value'])
                garden.save()
                return HttpResponse('')
        else:
            outlet = Outlet.objects.get(number=request.POST['outlet_number'], garden = garden)
            if request.POST['variable'] != "no_change": 
                setattr(outlet, request.POST['variable'], request.POST['new_value'])
                outlet.save()
                #Send exact same data to correct box
        
        # Changes of output based on style
        # Remember to add this to box_talk on the other side!

            if outlet.style == "PUMP":
                pump_json = outlet.pump_calculator()
                pump_reader = []
                for key in pump_json:
                    times = pump_json[key]
                    #create nice text for template lstrip and replace help get rid of the zero padding (05:00pm -> 5:00pm)
                    times_string = times['on'].strftime("%I:%M %p").lstrip("0").replace(" 0", " ") + "   to   " + times['off'].strftime("%I:%M %p").lstrip("0").replace(" 0", " ")
                    pump_reader.append(times_string)    
                return JsonResponse({"data":pump_reader})
            elif outlet.style == "UVB":
                uvb_start_time, uvb_end_time = outlet.uvb_calculator()
                text = uvb_start_time.strftime("%I:%M:%p").lstrip("0").replace(" 0", " ") + " to " + uvb_end_time.strftime("%I:%M:%p").lstrip("0").replace(" 0", " ")
                return JsonResponse({"data":text})
            else:
                return HttpResponse('')
                
def outlet_finder(garden_serial, outlet_number):
    garden = Garden.objects.get(pk=3)
    outlet = garden.outlet_set.get(number=outlet_number)
    context = {'garden':garden, 'outlet':outlet}
    return outlet
