import psycopg2
from psycopg2.extensions import AsIs
import pandas as pd

connectPG = psycopg2.connect("dbname=PGSEPS user=postgres password=eps host=10.60.0.245")            
cursorPG = connectPG.cursor()

datos = pd.DataFrame(columns=['puntos'])
#60357
for i in range(1,60358):
    cursorPG.execute("""SELECT string_agg(ST_AsText(point_geom), ',') AS points
            FROM (
            SELECT (ST_DumpPoints("SS_Tramos".geom)).geom AS point_geom
            FROM "SS_Tramos"
            WHERE "SS_Tramos".id = '%s'
            ) AS subquery""", (AsIs(i),))
    cota_inicial = cursorPG.fetchall()
    print(str(i) + " " + str(cota_inicial))
    
    nueva_fila = pd.DataFrame({'cota_ini':[cota_inicial[0]]})
    datos = pd.concat([datos, nueva_fila], ignore_index=True)
    
datos.to_csv('puntos Data.csv')

    