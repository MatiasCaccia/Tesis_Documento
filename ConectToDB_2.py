import time
import pyrebase
import numpy as np

def Conn2Firebase():
    config = {
      "apiKey": "UorA88wtBaPQjflBW9EkZLn3AHlHreUUReve4vNT",
      "authDomain": "datosruidoacustico.firebaseapp.com",
      "databaseURL": "https://datosruidoacustico-default-rtdb.firebaseio.com",
      "storageBucket": "datosruidoacustico.appspot.com"
    }
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    print('Conexión establecida')
    return db

db = Conn2Firebase()

filtr_type = 'T'

if filtr_type == 'O':
    cols = ("f31","f63","f125","f250","f500","f1000","f2000","f4000","f8000","Global","SoundExpLVL","Lpeak","Lmax","Lmin","hora","min","seg","Temp","CPU","RAM","MEMO")
else:
    cols = ("f25", "f31", "f40", "f50", "f63", "f80", "F100", "f125", "f160", "f200", "f250", "f315", "f400", "f500", "f630", 
            "f800", "f1000", "f1250", "f1600", "f2000", "f2500", "f3150", "f4000", "f5000", "f6300", "f8000", "f10000",
            "Global","SoundExpLVL","Lpeak","Lmax","Lmin","hora","min","seg","Temp","CPU","RAM","MEMO")
    
sumita3 = np.array([38.99, 38.34, 42.23, 41.38, 33.95, 35.55, 42.48, 44.85, 50.73, 55.05, 45.89, 52.94, 54.39, 55.73, 59.25, 57.14, 44.47, 46.71, 40.76, 36.1, 40.47, 38.49, 36.03, 31.68, 33.08, 34.11, 32.75, 64.63, 65.63, 93.83, 67.25, 50.75, 12, 3, 48])
CorrTerc = np.array([-12.008, -11.148, -8.948, -8.45, -7.366, -6.012, -5.516, -5.766, -6.028, -5.348, -5.544, -5.188, -5.89, -5.56, -5.136, -5.2, -5.626, -5.332, -5.42, -5.256, -5.206, -6.068, -4.798, -3.89, -2.454, -0.054, 2.368])

a = dict(zip(cols,sumita3))

while True:
  data = a
  db.child("Sensor1").child("1-set").set(data)
  db.child("Sensor1").child("2-push").push(data)
  time.sleep(2)


# import pymysql

# conn = pymysql.connect(host = 'db4free.net', user = 'elmatiascege', passwd = 'EstebanLombera', db = 'ruidourbano')

# def crearTabla(p_f,p_t,filtro,detector,mn,dd,hh,mm,ss):
#     myCursor = conn.cursor()
#     nombre_Tabla = str(p_f) + str(p_t) + str(filtro) + str(detector) + "_2021_" + str(mn) + "_"+ str(dd) + "_" + str(hh) +"_"+ str(mm)+"_"+ str(ss)
#     if filtro == 'O':
#         myCursor.execute("CREATE TABLE " + str(p_f) + str(p_t) + str(filtro) + str(detector) +
#                          "_2021_" + str(mn) + "_"+ str(dd) + "_" + str(hh) +"_"+ str(mm)+"_"+ str(ss) +"""
#             (
#             f31 REAL,
#             f63 REAL,
#             f125 REAL,
#             f250 REAL,
#             f500 REAL,
#             f1000 REAL,
#             f2000 REAL,
#             f4000 REAL,
#             f8000 REAL,
#             Global REAL,
#             SoundExpLVL REAL,
#             Lpeak REAL,
#             Lmax REAL,
#             Lmin REAL,
#             hora REAL,
#             min REAL,
#             seg REAL,
#             Temp REAL,
#             CPU REAL,
#             RAM REAL,
#             MEMO REAL
#             )
#             """)
#     else:
#         myCursor.execute("CREATE TABLE " + str(p_f) + str(p_t) + str(filtro) + str(detector) +
#                          "_2021_" + str(mn) + "_"+ str(dd) + "_" + str(hh) +"_"+ str(mm)+"_"+ str(ss) +"""
#             (
#             f25 REAL,
#             f31 REAL,
#             f40 REAL,
#             f50 REAL,
#             f63 REAL,
#             f80 REAL,
#             F100 REAL,
#             f125 REAL,
#             f160 REAL,
#             f200 REAL,
#             f250 REAL,
#             f315 REAL,
#             f400 REAL,
#             f500 REAL,
#             f630 REAL,
#             f800 REAL,
#             f1000 REAL,
#             f1250 REAL,
#             f1600 REAL,
#             f2000 REAL,
#             f2500 REAL,
#             f3150 REAL,
#             f4000 REAL,
#             f5000 REAL,
#             f6300 REAL,
#             f8000 REAL,
#             f10000 REAL,
#             Global REAL,
#             SoundExpLVL REAL,
#             Lpeak REAL,
#             Lmax REAL,
#             Lmin REAL,
#             hora REAL,
#             min REAL,
#             seg REAL,
#             Temp REAL,
#             CPU REAL,
#             RAM REAL,
#             MEMO REAL
#             )
#             """)
#     conn.commit()
#     conn.close()
#     return nombre_Tabla, print("Tabla creada")
