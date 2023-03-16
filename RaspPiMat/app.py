import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import pyrebase
import matplotlib.pyplot as plt
import pandas as pd
import requests
import json
import time
import datetime

#google real time database credentials and connection
cred = credentials.Certificate("tempmeasure-ac038-firebase-adminsdk-btvrw-8575135791.json")
app = firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://tempmeasure-ac038-default-rtdb.firebaseio.com/'
})

Config = {
    'apiKey': "AIzaSyBUycM5nuDdgq8T1vUE3yCHZcOLNqh5lYY",
    'authDomain': "tempmeasure-ac038.firebaseapp.com",
    'databaseURL': "https://tempmeasure-ac038-default-rtdb.firebaseio.com",
    'projectId': "tempmeasure-ac038",
    'storageBucket': "tempmeasure-ac038.appspot.com",
    'messagingSenderId': "679963048653",
    'appId': "1:679963048653:web:79f1214d6e6aa0a97ac784",
    'measurementId': "G-KFV33TYDVW",
    'serviceAccount':'tempmeasure-ac038-firebase-adminsdk-btvrw-8575135791.json'
}

firebase_storage = pyrebase.initialize_app(Config)
storage = firebase_storage.storage()

def time():
    #retrieving Eastern Standard time
    ts = time.time()
    systime = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%dT%H:%M:%S')
    print(systime)

def data(Data1, Data2, Min, Max):
    humidity = []
    temperature = []
    timeh = []
    timet = []

    #refrencing the sensor data child nose
    ref = db.reference('sensor_data/aht10')
    rawdata = ref.get()

    formatedMin = Min.split('-')
    ReqYearMin = int(formatedMin[0])
    ReqMonthMin = int(formatedMin[1])
    ReqDayMin = int(formatedMin[2])

    formatedMax = Max.split('-')
    ReqYearMax = int(formatedMax[0])
    ReqMonthMax = int(formatedMax[1])
    ReqDayMax = int(formatedMax[2])

    if Data1 == 'InHumid' or Data2 == 'InHumid':
        #retrieving the humidity data
        #list the keys of the returned dictionary        
        rawhumidity = rawdata['humidity']
        Hkeys = list(rawhumidity.keys())

        #storing humidity and temperture data as well as there respective time
        #in the list
        for i in range(len(Hkeys)):
            humidityTime = rawhumidity[Hkeys[i]]['timestamp']
            HumTimeDate = humidityTime.split('T')
            YearMonthDayH = HumTimeDate[0].split('-')
            YearH = int(YearMonthDayH[0])
            MonthH = int(YearMonthDayH[1])
            DayH = int(YearMonthDayH[2])

            if ReqYearMin <= YearH and ReqYearMax >= YearH and ReqMonthMin <= MonthH and ReqMonthMax >= MonthH and ReqDayMin <= DayH and ReqDayMax >= DayH:
                humidity.append(rawhumidity[Hkeys[i]]['humidity'])
                timeh.append(rawhumidity[Hkeys[i]]['timestamp'])

    if Data1 == 'InTemp' or Data2 == 'InTemp':
    #same thing we did with humidity but with temperature
        rawtemp = rawdata['temperature']
        Tkeys = list(rawtemp.keys())
 
        for i in range(len(Tkeys)):
            temperatureTime = rawtemp[Tkeys[i]]['timestamp']
            TempTimeDate = temperatureTime.split('T')
            YearMonthDayT = TempTimeDate[0].split('-')
            YearT = int(YearMonthDayT[0])
            MonthT = int(YearMonthDayT[1])
            DayT = int(YearMonthDayT[2])

            if  ReqYearMin <= YearT and ReqYearMax >= YearT and ReqMonthMin <= MonthT and ReqMonthMax >= MonthT and ReqDayMin <= DayT and ReqDayMax >= DayT:
                temperature.append(rawtemp[Tkeys[i]]['temp'])
                timet.append(rawtemp[Tkeys[i]]['timestamp'])

    return timeh, humidity, timet, temperature

def Bronx():
    bronxtemp = []
    bronxtime = []

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
            for i in range(len(periodData)):
                BronxCelcius = (int(periodData[i]['temperature'])-32)*(5/9)
                bronxtemp.append(BronxCelcius)
                bronxtime.append(periodData[i]['startTime'])
    return bronxtime, bronxtemp
    
def plotting(x, y, Date, OutT, task):
    if task == 'none':
        fig = plt.figure()
        plt.plot(x, y)
    else:
        plt.plot(x, y)
        plt.plot(Date, OutT)
    # plt.figure(1)
    # plt.plot(bronxtime, bronxtemp, label='Bronx Temperature')
    # plt.figure(2)
    # plt.plot(timet, temperature, label='House Temperature')
    plt.savefig('Graph')

    storage.child('Graph.png').put('Graph.png')

    #plt.show()

req = db.reference('Request/')
Mam = True
while Mam:
    pend = req.get()
    if pend['Task'] == 'Requested':
        dataset1 = pend['Data1']
        dataset2 = pend['Data2']
        Min = pend['Min']
        Max = pend['Max']
        GraphData = data(dataset1, dataset2, Min, Max)
        Bronx = Bronx()
        if dataset1[:-5] == 'Humid' or dataset2[:-5] == 'Humid':
            plotting(GraphData[0], GraphData[1], Bronx[0], Bronx[1], pend['Data2'])
        else:
            plotting(GraphData[2], GraphData[3], Bronx[0], Bronx[1], pend['Data2'])
    #Completed = req.child('Task')
    req.update({
        'Status':'Completed',
        'Task':'Idling'
    })
    time.sleep(60)