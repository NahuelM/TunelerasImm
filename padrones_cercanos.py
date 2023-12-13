# "id"
# 63319
import psycopg2
from psycopg2.extensions import AsIs
import pandas as pd

connectPG = psycopg2.connect("dbname=PGSEPS user=postgres password=eps host=10.60.0.245")            
cursorPG = connectPG.cursor()

datos = pd.DataFrame()

for i in range(1, 63320):
    cursorPG.execute("""SELECT ST_Distance(p.geom, t.geom) AS distance, p.id, p.padron, p.altura
                    FROM "padrones2023" p 
                    JOIN "SS_Tramos" t ON t.id = '%s'
                    WHERE ST_Distance(p.geom, t.geom) <= 100
                    ORDER BY distance""", (AsIs(i),))
    padrones = cursorPG.fetchall()
    #print(str(i))
    
    if padrones != []:  
        list_id = []
        list_padron = []
        list_alturas = []
        for j in range(0, len(padrones)):
            list_id.append(padrones[j][1])
            list_padron.append(padrones[j][2])
            list_alturas.append(padrones[j][3])
            print(padrones[j], j)
        nueva_fila = pd.DataFrame({'id_padron':[list_id], 'nro_padron':[list_padron], 'alturas':[list_alturas]})
    else:
        nueva_fila = None
        
    datos = pd.concat([datos, nueva_fila], ignore_index=True)
datos.to_csv('padronesCercanos2 Data.csv')