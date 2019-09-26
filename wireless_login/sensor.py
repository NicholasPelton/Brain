import serial
import time

def read_serial(ser):
    while True:
        if ser.inWaiting() > 0:
            break;
        time.sleep(0.5)
    return ser.readline()

device = "/dev/ttyUSB0"
buadrate = 9600
try:
    ser = serial.Serial(device, buadrate, timeout=1)
    time.sleep(2) #wait for the Arduino to init

    ser.write(b'0')
    num = int(read_serial(ser))

    for x in range(0,num):
        number = str(x+1)
        print(number)
        number = number.encode()
        ser.write(number)
        type = read_serial(ser).decode("utf-8")
        reading = read_serial(ser).decode("utf-8")
        unit = read_serial(ser).decode("utf-8")
        print(type,reading,unit)
except:
    print("Nothing plugged in here")
