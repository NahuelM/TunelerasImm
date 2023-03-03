import pandas as pd


csv_data_tramos = pd.read_csv('Datos.csv', delimiter=',')
datos_arreglados = pd.DataFrame(columns=[ 'tipo_tra', 'tiposec', 'greates', 'least', 'zarriba', 'zabajo', 'logitud'])

i = 0
print(str(csv_data_tramos.shape[0]))
while i <= csv_data_tramos.shape[0] - 1:
    datos_id = csv_data_tramos.iloc[int(i)][0]
    dato_id_sig = csv_data_tramos.iloc[int(i+1)][0]
    datos_read = csv_data_tramos.iloc[int(i)][1:8]
    datos = [datos_read]
    dif = int(dato_id_sig) - int(datos_id)
    print(str(dif == 1) + ' ' + str(i) + ' ' + str(dif))
    if(dif == 1):
        nueva_fila = pd.DataFrame({'tipo_tra':[datos_read[0]], 'tiposec':[datos_read[1]], 'greates':[datos_read[2]], 'least':[datos_read[3]], 'zarriba':[datos_read[4]], 'zabajo':[datos_read[5]], 'logitud':[datos_read[6]]})
        datos_arreglados = pd.concat([datos_arreglados, nueva_fila], ignore_index = True)
        i += 1
    else:
        nueva_fila = pd.DataFrame({'tipo_tra':[datos_read[0]], 'tiposec':[datos_read[1]], 'greates':[datos_read[2]], 'least':[datos_read[3]], 'zarriba':[datos_read[4]], 'zabajo':[datos_read[5]], 'logitud':[datos_read[6]]})
        datos_arreglados = pd.concat([datos_arreglados, nueva_fila], ignore_index = True)
        for k in range(1, dif):
            #print('range filas nulas:  '+ str(i)  + ' to ' + str(i+(index-i)) + ' ' + str(k))
            nueva_fila = pd.DataFrame({'tipo_tra':[0], 'tiposec':[0], 'greates':[0], 'least':[0], 'zarriba':[0], 'zabajo':[0], 'logitud':[0]})
            datos_arreglados = pd.concat([datos_arreglados, nueva_fila], ignore_index = True)
            i += 1
            


datos_arreglados.to_csv('Datos_arreglados.csv')