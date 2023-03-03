import psycopg2
from psycopg2.extensions import AsIs
import pandas as pd

connectPG = psycopg2.connect("dbname=PGSEPS user=postgres password=eps host=10.60.0.245")            
cursorPG = connectPG.cursor()

datos = pd.DataFrame(columns=['cota_ini', 'id_punto_ini', 'cota_fin', 'id_punto_fin'])
#59363
for i in range(1,59363):
    cursorPG.execute("""SELECT cota, id FROM "SS_Puntos" p WHERE CAST((SELECT ST_X(ST_GeometryN(p.geom,1))) AS numeric) = 
                 (SELECT CAST((SELECT ST_X(ST_StartPoint(ST_GeometryN(t.geom,1)))) AS numeric) FROM "SS_Tramos" t WHERE CAST(id AS character varying) = '%s');""", (AsIs(i),))
    cota_inicial = cursorPG.fetchall()
    
    cursorPG.execute("""SELECT cota, id FROM "SS_Puntos" p WHERE CAST((SELECT ST_X(ST_GeometryN(p.geom,1))) AS numeric) = 
                    (SELECT CAST((SELECT ST_X(ST_EndPoint(ST_GeometryN(t.geom,1)))) AS numeric) FROM "SS_Tramos" t WHERE CAST(id AS character varying) = '%s');""", (AsIs(i),))
    cota_final = cursorPG.fetchall()
    if(cota_final == []):
        print('cota final None')
        cota_final = [['', '']]
        print(str(cota_final))
        
    if(cota_inicial == []):
        print('cota inicial  None')
        cota_inicial = [['', '']]
        print(str(cota_inicial))
    #print('cota_ini '+ str(cota_inicial[0][0]) +' id_punto_ini ' + str(cota_inicial[0][1]) + ' cota_fin '+ str(cota_final[0][0]) + ' id_punto_fin ' + str(cota_final[0][1]) + '  ' + str(i))
    print(str(cota_inicial) + ' ' + str(cota_final)  + '  ' + str(i))
    nueva_fila = pd.DataFrame({'cota_ini':[cota_inicial[0][0]], 'id_punto_ini':[cota_inicial[0][1]], 'cota_fin':[cota_final[0][0]], 'id_punto_fin':[cota_final[0][1]]})
    datos = pd.concat([datos, nueva_fila], ignore_index=True)
    
datos.to_csv('puntos Data.csv')

    