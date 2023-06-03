import requests
import datetime
import time

def HourTracker():
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print(current_time)
    RawClockCount = current_time.split(':')
    if int(RawClockCount[1]) and int(RawClockCount[2]) != 0:
        time.sleep(1)
        HourTracker()

def Bronx():
    #making a request for the meta data from my coordinates
    #then storing the temperature, humadity, and time stamps from my area
    rawmeta = requests.get('https://api.weather.gov/points/40.8104808,-73.9250748')
    print(rawmeta.status_code)
    if rawmeta.status_code == 200:
        print('meta data has been recieved')
        meta = rawmeta.json()
        rawhourlyforcast = requests.get(meta['properties']['forecastHourly'])
        if rawhourlyforcast.status_code == 200:
            print('hourly forcast recieved')
            hourlyforecast = rawhourlyforcast.json()
            periodData = hourlyforecast['properties']['periods']
            BronxCelcius = (int(periodData[0]['temperature'])-32)*(5/9)
            bronxtime = periodData[0]['startTime']
        else:
            print(rawmeta.status_code + 'error /n reatempting in 10 seconds')
            time.sleep(10)
            Bronx()
    else:
        print(rawmeta.status_code + 'error /n reatempting in 10 seconds')
        time.sleep(10)
        Bronx()
    return bronxtime, BronxCelcius

while True:
    print(datetime.date.today())
    Coin = HourTracker()
    BronxData = Bronx()
    Coin = False
    