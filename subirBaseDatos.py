import numpy as np
import pymysql
import time
import psutil

def get_cpu_temp():
    result = 0.0
    with open('/sys/class/thermal/thermal_zone0/temp') as f:
        line = f.readline().strip()
    if line.isdigit():
        result = float(line) / 1000
    return result

def subirDatos(tiempo,contador,mn,dd,filtr_type, nombre_Tabla):
    q = np.load('/home/pi/Documents/2021_'+str(mn)+'/'+str(dd)+'.npy')
    #valores = contador*tiempo - contador # ACA MATI!!
    valores = (contador + 1) *tiempo
    asdf = q[(valores*-1):]
    sumita = asdf
    sumita1 = 10**(0.1*sumita)
    sumita2 = np.array([sum(x) for x in zip(*sumita1)])
    sumita3 = list(np.around(10*np.log10(sumita2/len(sumita)),2))
    Lpico = 0
    Nmax = 0
    Nmin = 0
    for n in range(0,len(asdf)):
        if asdf[n][-6] > Lpico:
            Lpico = asdf[n][-6]
        if asdf[n][-5] > Nmax:
            Nmax = asdf[n][-5]
        if asdf[n][-4] < Nmax:
            Nmin = asdf[n][-4]
    sumita3[-4] = np.around(Nmin,2)
    sumita3[-5] = np.around(Nmax,2)
    sumita3[-6] = np.around(Lpico,2)
    sumita3[-3:-1] = asdf[-1][-3:-1]
    sumita3[-1] = asdf[-1][-1]
    #print(sumita3)
    Temp = np.around(get_cpu_temp(),2)
    sumita3.append(Temp)
    Perf_CPU = np.around(psutil.cpu_percent(),2)
    sumita3.append(Perf_CPU)
    Perf_RAM = np.around(psutil.virtual_memory().percent,2)
    sumita3.append(Perf_RAM)
    Perf_MEMO = np.around(psutil.virtual_memory().available * 100 / psutil.virtual_memory().total,2)
    sumita3.append(Perf_MEMO)
    """
        Comienza a subir los datos a la red
    """
    #start = time.time()
    conn = pymysql.connect(host = 'db4free.net', user = 'elmatiascege', passwd = 'EstebanLombera', db = 'ruidourbano')
    myCursor = conn.cursor()
    if filtr_type == 'O':
        cols = ("f31","f63","f125","f250","f500","f1000","f2000","f4000","f8000","Global","SoundExpLVL","Lpeak","Lmax","Lmin","hora","min","seg","Temp","CPU","RAM","MEMO")
    else:
        cols = ("f25", "f31", "f40", "f50", "f63", "f80", "F100", "f125", "f160", "f200", "f250", "f315", "f400", "f500", "f630", 
                "f800", "f1000", "f1250", "f1600", "f2000", "f2500", "f3150", "f4000", "f5000", "f6300", "f8000", "f10000",
                "Global","SoundExpLVL","Lpeak","Lmax","Lmin","hora","min","seg","Temp","CPU","RAM","MEMO")
    a = dict(zip(cols,sumita3))
    sql = 'INSERT INTO '+ nombre_Tabla[0] +' ({fields}) VALUES ({values});'
    fields = ', '.join(a.keys())
    values = ', '.join(['"{0}"'.format(value) for value in a.values()])
    composed_sql = sql.format(fields=fields, values=values)
    myCursor.execute(composed_sql)   
    print("Tabla actualizada")
    conn.commit()
    conn.close()
    #end = time.time()
    #print(end - start)
    return