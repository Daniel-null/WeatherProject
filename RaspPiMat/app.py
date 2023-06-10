import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import pyrebase
import matplotlib.pyplot as plt
from matplotlib import dates as mpl_dates
import pandas as pd
import requests
import json
import time
import datetime
import threading

#google credentials and connection
#needed to make read and write request to googles real time database and storage
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

#using threading it will keep track of time. Every hour it will make a request to the
#bronx weaather api
def HourTracker():
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    #print(current_time)
    RawClockCount = current_time.split(':')
    if int(RawClockCount[1]) and int(RawClockCount[2]) != 0:
        time.sleep(1)
        HourTracker()
    else:
        return datetime.date.today()

#The data function makes a call to the realtime database and sorts through the data 
#and puts it all in a neat package that makes it easy to graph
def data(Data1, Data2, Min, Max):
    humidity = []
    temperature = []
    timeh = []
    timet = []
    BrTemp = []
    BrHum = []
    BrTimeT = []
    BrTimeH = []
    DataPacket = []

    #Before you make a call to the realtime database
    #you want to give python a reference to the location where the data we want to pull is
    ref = db.reference('sensor_data/aht10')
    rawdata = ref.get()

    BronxRef = db.reference('Bronx/')
    BronxInfo = BronxRef.get()

    #I split the dates and convert to intigers as this is ideal for comparisons
    formatedMin = Min.split('-')
    ReqYearMin = int(formatedMin[0])
    ReqMonthMin = int(formatedMin[1])
    ReqDayMin = int(formatedMin[2])

    formatedMax = Max.split('-')
    ReqYearMax = int(formatedMax[0])
    ReqMonthMax = int(formatedMax[1])
    ReqDayMax = int(formatedMax[2])

    #each if statment checks which data is requested. It then packages it and appends it
    #to the packet we will send back to the main thread
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
                humidity.append(float(rawhumidity[Hkeys[i]]['humidity']))
                timeh.append(rawhumidity[Hkeys[i]]['timestamp'])
        DataPacket.append('Inside Humidity')
        DataPacket.append('%')
        DataPacket.append(timeh)
        DataPacket.append(humidity)

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
                temperature.append(float(rawtemp[Tkeys[i]]['temp']))
                timet.append(rawtemp[Tkeys[i]]['timestamp'])
        DataPacket.append('Inside Temperature')
        DataPacket.append('Celcius')
        DataPacket.append(timet)
        DataPacket.append(temperature)

    if Data1 == 'OutHumid' or Data2 == 'OutHumid':
        #using the reference we want to store the keys to each data point
        BronxDates = list(BronxInfo.keys())

        for i in range(len(BronxDates)):
            DateTimeProc = BronxDates[i].split('T')
            BDate = DateTimeProc[0].split('-')
            BYear = int(BDate[0])
            BMonth = int(BDate[1])
            BDay = int(BDate[2])
            if  ReqYearMin <= BYear and ReqYearMax >= BYear and ReqMonthMin <= BMonth and ReqMonthMax >= BMonth and ReqDayMin <= BDay and ReqDayMax >= BDay:
                BrHum.append(float(BronxInfo[BronxDates[i]]['Humidity']))
                BrTimeH.append(BronxDates[i])
        DataPacket.append('OutDoor Humidity')
        DataPacket.append('%')
        DataPacket.append(BrTimeH)
        DataPacket.append(BrHum)

    if Data1 == 'OutTemp' or Data2 == 'OutTemp':
        BronxDates = list(BronxInfo.keys())

        for i in range(len(BronxDates)):
            DateTimeProc = BronxDates[i].split('T')
            BDate = DateTimeProc[0].split('-')
            BYear = int(BDate[0])
            BMonth = int(BDate[1])
            BDay = int(BDate[2])
            if  ReqYearMin <= BYear and ReqYearMax >= BYear and ReqMonthMin <= BMonth and ReqMonthMax >= BMonth and ReqDayMin <= BDay and ReqDayMax >= BDay:
                BrTemp.append(float(BronxInfo[BronxDates[i]]['Temperature']))
                BrTimeT.append(BronxDates[i])
                DataPacket.append('OutDoor Temperature')
                DataPacket.append('Celcius')
                DataPacket.append(BrTimeT)
                DataPacket.append(BrTemp)
    return DataPacket

#The bronx function makes a get request to the national weather api
def Bronx():
    #making a request for my weather data from my coordinates
    #then storing the temperature, humadity, and time stamps from my area
    rawmeta = requests.get('https://api.weather.gov/points/40.8104808,-73.9250748')
    #print(rawmeta.status_code)
    if rawmeta.status_code == 200:
        #print('meta data has been recieved')
        meta = rawmeta.json()
        rawhourlyforcast = requests.get(meta['properties']['forecastHourly'])
        if rawhourlyforcast.status_code == 200:
            #print('hourly forcast recieved')
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
    
#handles plotting the data requested and uploading it
def plotting(packet, Data1, Data2):
    print('started graphing')
    #checks for conditoning to plot a graph
    #all this code is to A) graoh the data and B) make it pretty
    if Data2 == 'None':
        plt.style.use('seaborn')
        packet[2] = pd.to_datetime(packet[2])
        plt.plot_date(packet[2], packet[3], marker='', linestyle='solid', label=packet[0])
        plt.ylabel(packet[1])
        plt.legend(loc='upper left')
        plt.gcf().autofmt_xdate()
        plt.gcf().set_size_inches(10, 7)
        #plt.tight_layout()
        plt.savefig('Graph')
        plt.clf()
    elif Data1[-5:] == Data2[-5:] or Data1[-4:] == Data2[-4:]:
        plt.style.use('seaborn')
        packet[2] = pd.to_datetime(packet[2])
        packet[6] = pd.to_datetime(packet[6])
        plt.plot_date(packet[2], packet[3], marker='', linestyle='solid', label=packet[0])
        plt.plot_date(packet[6], packet[7], marker='', linestyle='solid', label=packet[4])
        plt.ylabel(packet[1])
        plt.legend(loc='upper left')
        plt.gcf().autofmt_xdate()
        plt.gcf().set_size_inches(10, 7)
        #plt.tight_layout()
        plt.savefig('Graph')
        plt.clf()
    else:
        fig = plt.figure()
        plt.style.use('classic')
        ax = fig.add_subplot(111, label='1')
        ax2 = fig.add_subplot(111, label='2', frame_on=False)
        packet[2] = pd.to_datetime(packet[2])
        packet[6] = pd.to_datetime(packet[6])
        ax.plot_date(packet[2], packet[3], marker='', linestyle='solid', color='C0', label=packet[0])
        ax2.plot_date(packet[6], packet[7], marker='', linestyle='solid', color='C1', label=packet[4])
        ax.set_ylabel(packet[1])
        ax2.set_ylabel(packet[5])
        ax2.yaxis.set_label_position('right')
        ax2.set_xticks([])
        ax2.yaxis.tick_right()
        fig.legend(loc='upper left')
        plt.gcf().autofmt_xdate()
        plt.gcf().set_size_inches(10, 7)
        #fig.tight_layout()
        fig.savefig('Graph')
        plt.clf()
    #we then save the figure as a png and upload it to googles storage api
    storage.child('Graph.png').put('Graph.png')
    print('Graphing complete')

#uploads bronx data to database
def DataUpload(BronxData):
    DataRef = db.reference('Bronx/')
    CutDate = BronxData[0]
    DataFormat = {
        "Temperature":BronxData[1],
        "Humidity":BronxData[2]
    }
    DataRef.child(CutDate[:19]).set(DataFormat)
    #print('upload succeful')
    
#second soruce thread, handles the schedule for bronx data collection
def Clock():
    while True:
        HourTracker()
        BronxData = Bronx()
        DataUpload(BronxData)
        time.sleep(1)

#the main function thread, handles the process for packaging data and graphing
def dataproccessing():
    req = db.reference('Request/')
    while True:
        pend = req.get()
        if pend['Task'] == 'Requested':
            dataset1 = pend['Data1']
            dataset2 = pend['Data2']
            Min = pend['Min']
            Max = pend['Max']
            if dataset1 == dataset2:
                print('request denied')
            else:
                GraphData = data(dataset1, dataset2, Min, Max)
                print('request Recieved')
                plotting(GraphData, dataset1, dataset2)
        req.update({
            'Status':'Completed',
            'Task':'Idling'
        })
        time.sleep(5)

Thread1 = threading.Thread(target=Clock, args=())
Thread2 = threading.Thread(target=dataproccessing, args=())
Thread1.start()
Thread2.start()