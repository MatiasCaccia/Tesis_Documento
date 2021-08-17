"""
Descripción.
"""
try:
    import numpy as np
    import sounddevice as sd
    import threading
    from funciones import (filt_A, filt_oct, sum_db, busca_cal, slow,
                          busca_ajuste, niveles, rms_t, filt_C, 
                          Lpeak, Lmax, Lmin, rms_pond_t, filt_to,
                          escr_arr as escribir)
    from ConectToDB import (crearTabla)
    from time import localtime, time as tiempo
    from subirBaseDatos import subirDatos
    import sys
    import matplotlib.pyplot as plt
        
    print("Inicializando dispositivo.")
    sd.stop()
    # - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Parámetros por defecto
    fs = 48000
    sd.default.samplerate = fs
    sd.default.channels = 1
    sd.default.device = 'snd_rpi_simple_card'
    Lpeak_peak = 0
    Lmax_max = 0
    Lmin_min = 0
    # - - - - - - - - - - - - - - - - - - - - - - - - - -
    '''
    dur = input('Ingrese la duración en segundos:    ')
    dur = int(dur)
    pond_f = input('Ingrese la ponderacion frecuencial A, C o Z:    ')
    pond_t = input('Ingrese la ponderacion temporal S (slow), F (fast) o I (impulsive):    ')
    linexp = input('Ingrese el modo del detector: L (lineal) o E (exponencial)    ')
    filter_f = input('Filtrado por: O (octava) o T (tercio de octava):    ')
    '''
    dur = 10
    dur = int(dur)
    durN = int(fs*dur) # duración en muestras
    pond_f = 'A'
    pond_t = 'S'
    linexp = 'E'
    filter_f = 'T'
    if pond_f != 'A' and pond_f != 'C' and pond_f != 'Z':
        print('Ponderación frecuencial desconocida')
        sys.exit() #quit()
    '''
    if pond_t != 'S' and pond_t != 'F' and pond_t != 'I':
        print('Ponderación temporal desconocida')
        sys.exit()
    '''
    if filter_f != 'O' and filter_f != 'T':
        print('Filtrado desconocido')
        sys.exit()
    if linexp != 'L' and linexp != 'E':
        print('Detector desconocido')
        sys.exit()
    if pond_t == 'S' and pond_t != 'F' and pond_t != 'I':
        tempo = 1.0
    elif pond_t == 'F':
        tempo = 0.125
    elif pond_t == 'I':
        tempo = 0.035
    else:
        print('Ponderación temporal desconocida')
        sys.exit()
    # - - - - - - - - - - - - - - - - - - - - - - - - - -
    inicio = localtime(tiempo()) # tiempo de inicio del audio a analizar
    nombre_Tabla = crearTabla(pond_f,pond_t,filter_f,linexp,inicio.tm_mon,inicio.tm_mday,inicio.tm_hour,inicio.tm_min,inicio.tm_sec)
    # - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Creación de arreglos para los datos de salida del callback
    mat = np.array([])
    t = np.array([])
    niv_y = np.array([])
    buffer = np.array([])
    contador = 0
    # - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Recuperación de valores de calibración y compensación del dispositivo.
    vcal, ncal = busca_cal()
    #ncal = 94.0
    # - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Funciones útiles para la ejecución de los ciclos de callback.
    def agregar_t(t, n):
        """ Recibe un arreglo lineal comprendiendo una hora, minuto y segundo,
        y la cantidad de filas a entregar, y entrega a la salida un arreglo
        en cuya primera fila está el arreglo ingresado, y en cada una de las
        subsiguientes se agrega un segundo. """
        n = int(n)
        t_agr = np.zeros([n, 3])
        t_agr[0,:] = t
        for i in np.arange(n-1):
            if not t_agr[i,2] == 59:
                t_agr[i+1,2] = t_agr[i,2]+1
                t_agr[i+1,1] = t_agr[i,1]
                t_agr[i+1,0] = t_agr[i,0]
            else:
                t_agr[i+1,2] = 0
                if not t_agr[i,1] == 59:
                    t_agr[i+1,1] = t_agr[i,1]+1
                    t_agr[i+1,0] = t_agr[i,0]
                elif not t_agr[i,0] == 23:
                    t_agr[i+1,1] = 0
                    t_agr[i+1,0] = t_agr[i,0]+1
                else:
                    t_agr[i+1,1] = 0
                    t_agr[i+1,0] = 0
        return t_agr

    def separar(yy, mn, dd, t_fin, mat):
        """ Escritura de datos por separado de cambiar el día durante la ejecución.
        Recibe el año, mes y día de inicio de la grabación, la estructura de
        tiempos del final de la grabación y la matriz con los datos a exportar. """
        idx = int(np.min(np.where(mat[:,0]==0)[0]))
        mat_prim = mat[:idx,:]
        mat_sec = mat[idx:,:]
        escribir(yy, mn, dd, mat_prim)
        escribir(t_fin.tm_year, t_fin.tm_mon, t_fin.tm_mday, mat_sec)
        return
    # - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Funciones específicas de ejecución del dispositivo.
    def callback(indata, frames, time, status):
        """ Función principal para la ejecución continua del dispositivo
        utilizando threading. """
        global buffer, contador
        buffer = indata
        thr = threading.Thread(name='Procesado por threading', target=procesado, args=[buffer,contador])
        thr.start()
        if contador < 1:
            contador = contador + 1
        else:
            contador = 0
        buffer = np.array([])
        return
    
    def procesado(x,contador):
        # Manejo de datos temporales.
        ahora = tiempo() # instante de arranque para obtener la duración del ciclo
        print('\nCalculando ...')
        inicio = localtime(tiempo()-len(x)/fs) # tiempo de inicio del audio a analizar
        fin = localtime() # tiempo final del audio a analizar
        t_inic = np.array([inicio.tm_hour, inicio.tm_min, inicio.tm_sec])
        dd = inicio.tm_mday
        mn = inicio.tm_mon
        yy = inicio.tm_year
        # //////////////////////////////////
        """ Función principal para el procesado del audio a analizar para cada
        ciclo de ejecución, 'x'. """
        # Procesamiento de la señal de audio.
        # ////////////////////////////////// PONDERACION A,C,Z
        if pond_f == 'A':
            xA = filt_A(x.reshape(-1)) # ponderación 'A'
        elif pond_f == 'C':
            xA = filt_C(x.reshape(-1)) # ponderación 'C'
        elif pond_f == 'Z': 
            xA = x.reshape(-1) # ponderación 'z'
        Lpico = Lpeak(xA,vcal,ncal)
        Nmax, Nmin = Lmax(xA,vcal,ncal)
        # //////////////////////////////////
        # Ponderación temporal de la señal de entrada
        #plt.plot(10*np.log10((xA/0.00002)**2))
        #if linexp == 'L':
            #xA = xA
        #elif linexp == 'E': 
            #xA = np.sqrt(slow(xA))
            #xA = (slow((xA)))
            #xA = (xA)
        #plt.plot(10*np.log10((xA/0.00002)**2))
        #plt.show()
        #print('TEMPORAL')
        #print(xA)
        #print(len(xA))
        # //////////////////////////////////
        if filter_f == 'O':
            nivs_y = filt_oct(xA) # filtrado por octavas
        elif filter_f == 'T':
            nivs_y = filt_to(xA) # filtrado por tercio
        # //////////////////////////////////
        if linexp == 'L':
            nivs_y = nivs_y
            niv_y = np.transpose(niveles(rms_t(nivs_y), vcal, ncal))
        elif linexp == 'E':
            nivs_y = slow(nivs_y)
            niv_y = np.transpose(niveles(rms_t(nivs_y), vcal, ncal))
            #niv_y = np.transpose(niveles(rms_pond_t(x,1.0), vcal, ncal))
        # Cálculo de niveles de presión con compensación.
        #niv_y = np.transpose(niveles(rms_t(nivs_y), vcal, ncal))
        # //////////////////////////////////
        # Agregado de niveles globales.
        Lpico = Lpico*np.ones((niv_y.shape[0],1))
        Nmax = Nmax*np.ones((niv_y.shape[0],1))
        Nmin = Nmin*np.ones((niv_y.shape[0],1))
        glob_y = np.apply_along_axis(sum_db, 1, niv_y).reshape(niv_y.shape[0],1)
        niv_y_0 = np.append(niv_y,glob_y,axis =1) #Agrego el GLOBAL
        aux1 = glob_y + np.log10(int(dur))
        niv_y_1 = np.append(niv_y_0,aux1,axis =1) #Agrego el SEL
        niv_y_2 = np.append(niv_y_1,Lpico,axis =1) #Agrego el Pico
        niv_y_3 = np.append(niv_y_2,Nmax,axis =1) #Agrego el Maximo
        niv_y_4 = np.append(niv_y_3,Nmin,axis =1) #Agrego el Minimo
        # Agregado de tiempos de inicio para la matriz de salida.
        t = agregar_t(t_inic,dur)
        niv_y_5 = np.append(niv_y_4,t,axis =1)
        mat = niv_y_5
        #print('FINAL')
        #print(niv_y_5)
        # Escritura de la matriz de salida en el archivo de volcado '.npy'.
        if inicio.tm_mday == fin.tm_mday: # si hubo cambio de día, separo los resultados
            escribir(yy, mn, dd, mat) # si no escribo directo la matriz
        elif inicio.tm_mday != fin.tm_mday:
            separar(yy, mn, dd, fin, mat)
        # Impresión en consola de tiempo de ejecución y nivel global del ciclo.
        print('\nEjecución de ciclo completa. \nTiempo de ejecución : ' + str(np.around(tiempo() - ahora, 2)) + ' s\n')
        print('\nContador va: ' + str(contador))
        # //////////////////////////////////
        #else:
            #print('Llegue a 2, a ver si se ejecuta lo que hiciste')
            #subirDatos(int(dur),contador,mn,dd)
        #print(contador)
        contador = 1
        subirDatos(int(dur),contador,mn,dd,filter_f, nombre_Tabla)
        '''
        if contador == 1:
            subirDatos(int(dur),contador,mn,dd,filter_f, nombre_Tabla)
            contador = 0
        return
        '''
    # - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Inicialización del stream de audio con sounddevice.
    with sd.InputStream(callback=callback, blocksize=durN):
        print("\nEjecutando. Presione 'q' para finalizar.")
        while True:
            response = input()
            if response in ('k', 'K'):
                print("\nEjecución de calibración.")
                # FUNCION DE CALIBRACION
                continue
            elif response in ('q', 'Q'):
                #wavefile.close()
                print("\nEjecución finalizada.")
                break

except KeyboardInterrupt:
    print('\nInterrupción de teclado. Ejecución finalizada.')
except Exception as e:
    print(type(e).__name__ + ': ' + str(e))
