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
import threading

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

def HourTracker():
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print(current_time)
    RawClockCount = current_time.split(':')
    if int(RawClockCount[1]) and int(RawClockCount[2]) != 0:
        time.sleep(1)
        HourTracker()
    else:
        return datetime.date.today()

def Localtime():
    #retrieving Eastern Standard time
    ts = time.time()
    systime = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%dT%H:%M:%S')
    print(systime)

def data(Data1, Data2, Min, Max):
    humidity = []
    temperature = []
    timeh = []
    timet = []
    BrTemp = []
    BrHum = []
    BrTime = []
    #refrencing the sensor data child node
    ref = db.reference('sensor_data/aht10')
    rawdata = ref.get()

    BronxRef = db.reference('Bronx/')
    BronxInfo = BronxRef.get()

    #int of the range of dates requested
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

    if Data1 == 'OutHumid' or Data2 == 'OutHumid':
        BronxDates = list(BronxInfo.keys())

        for i in range(len(BronxDates)):
            DateTimeProc = BronxDates[i].split('T')
            BDate = DateTimeProc[0].split('-')
            BYear = int(BDate[0])
            BMonth = int(BDate[1])
            BDay = int(BDate[2])
            if  ReqYearMin <= BYear and ReqYearMax >= BYear and ReqMonthMin <= BMonth and ReqMonthMax >= BMonth and ReqDayMin <= BDay and ReqDayMax >= BDay:
                BrHum.append(BronxInfo[BronxDates[i]]['Humidity'])
                BrTime.append(BronxDates[i])

    if Data1 == 'OutTemp' or Data2 == 'OutTemp':
        BronxDates = list(BronxInfo.keys())

        for i in range(len(BronxDates)):
            DateTimeProc = BronxDates[i].split('T')
            BDate = DateTimeProc[0].split('-')
            BYear = int(BDate[0])
            BMonth = int(BDate[1])
            BDay = int(BDate[2])
            if  ReqYearMin <= BYear and ReqYearMax >= BYear and ReqMonthMin <= BMonth and ReqMonthMax >= BMonth and ReqDayMin <= BDay and ReqDayMax >= BDay:
                BrTemp.append(BronxInfo[BronxDates[i]]['Temperature'])
                if not BrTime:
                    BrTime.append(BronxDates[i])

    return timeh, humidity, timet, temperature, BrTemp, BrHum, BrTime

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
            Bronxtime = periodData[0]['startTime']
            BronxHumidity = periodData[0]['relativeHumidity']['value']
        else:
            print(rawmeta.status_code + 'error /n reatempting in 10 seconds')
            time.sleep(10)
            Bronx()
    else:
        print(rawmeta.status_code + 'error /n reatempting in 10 seconds')
        time.sleep(10)
        Bronx()
    return Bronxtime, BronxCelcius, BronxHumidity
    
def plotting(x, y, Date, OutT, task):
    if task == 'None':
        fig = plt.figure()
        plt.plot(x, y)
    else:
        plt.plot(x, y)
        plt.plot(Date, OutT)
    plt.savefig('Graph')

    storage.child('Graph.png').put('Graph.png')
    print('Graphing complete')
    #plt.show()

def DataUpload(BronxData):
    DataRef = db.reference('Bronx/')
    DataFormat = {
        "Temperature":BronxData[1],
        "Humidity":BronxData[2]
    }
    DataRef.child(BronxData[0]).set(DataFormat)
    
def Clock():
    while True:
        HourTracker()
        BronxData = Bronx()
        DataUpload(BronxData)

#must fix datapipline
def dataproccessing():
    req = db.reference('Request/')
    BronxRef = db.reference('Bronx') 
    while True:
        pend = req.get()
        if pend['Task'] == 'Requested':
            dataset1 = pend['Data1']
            dataset2 = pend['Data2']
            Min = pend['Min']
            Max = pend['Max']
            GraphData = data(dataset1, dataset2, Min, Max)

            if dataset1[:-5] == 'Humid' or dataset2[:-5] == 'Humid':
                plotting(GraphData[0], GraphData[1], BronxData[0], BronxData[1], pend['Data2'])
            else:
                plotting(GraphData[2], GraphData[3], BronxData[0], BronxData[1], pend['Data2'])
        #Completed = req.child('Task')
        req.update({
            'Status':'Completed',
            'Task':'Idling'
        })
        time.sleep(60)

Thread1 = threading.Thread(target=Clock, args=())
Thread2 = threading.Thread(target=dataproccessing, args=())
Thread1.start()
Thread2.start()