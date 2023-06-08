import firebase_admin
from firebase_admin import credentials
from firebase_admin import db


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

RefTime = '56'
BronxData = {
    "Number":55,
    "second":66
}

DataRef = db.reference('Bronx/')
DataRef.child(RefTime).set(BronxData)

Datpacket = []
Datpacket.extend(55, 60)
print(Datpacket)