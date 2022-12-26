import plotly.express as px
import plotly.graph_objects as go
import plotly 
from plotly.graph_objs import Mesh3d
from plotly.subplots import make_subplots
import plotly.offline as off

import psycopg2
from psycopg2.extensions import AsIs
import math
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

connectPG = psycopg2.connect("dbname=PGSEPS user=postgres password=eps host=10.60.0.245")            
cursorPG = connectPG.cursor()
idTramo = "97"
# datos del tramo
cursorPG.execute("""SELECT tipotra, tiposec, GREATEST(dim1,dim2), LEAST(dim1,dim2), zarriba, zabajo, longitud FROM public."SS_Tramos"
                    WHERE CAST(id AS character varying) = '%s';""", (AsIs(idTramo),))
                    
datos = cursorPG.fetchall()
#print(datos)
# cota de terreno (punto inicial)
cursorPG.execute("""SELECT cota, id FROM "SS_Puntos" p WHERE CAST((SELECT ST_X(ST_GeometryN(p.geom,1))) AS numeric) = (SELECT CAST((SELECT ST_X(ST_StartPoint(ST_GeometryN(t.geom,1)))) AS numeric) FROM "SS_Tramos" t WHERE CAST(id AS character varying) = '%s');""", (AsIs(idTramo),))
cotaInicial = cursorPG.fetchall()
#print("cotaInicical: " + str(cotaInicial))
cursorPG.execute("""SELECT cota, id FROM "SS_Puntos" p WHERE CAST((SELECT ST_X(ST_GeometryN(p.geom,1))) AS numeric) = (SELECT CAST((SELECT ST_X(ST_StartPoint(ST_GeometryN(t.geom,1)))) AS numeric) FROM "SS_Tramos" t WHERE CAST(id AS character varying) = '%s');""", (AsIs(idTramo),))
existe1 = cursorPG.fetchone()
#print("existe1: " + str(existe1))


# punto final
cursorPG.execute("""SELECT cota, id FROM "SS_Puntos" p WHERE CAST((SELECT ST_X(ST_GeometryN(p.geom,1))) AS numeric) = 
                (SELECT CAST((SELECT ST_X(ST_EndPoint(ST_GeometryN(t.geom,1)))) AS numeric) FROM "SS_Tramos" t WHERE CAST(id AS character varying) = '%s');""", (AsIs(idTramo),))
cotaFinal = cursorPG.fetchall()
#print("cotaFinal: " + str(cotaFinal))
# punto final
cursorPG.execute("""SELECT cota, id FROM "SS_Puntos" p WHERE CAST((SELECT ST_X(ST_GeometryN(p.geom,1))) AS numeric) = 
                (SELECT CAST((SELECT ST_X(ST_EndPoint(ST_GeometryN(t.geom,1)))) AS numeric) FROM "SS_Tramos" t WHERE CAST(id AS character varying) = '%s');""", (AsIs(idTramo),))
existe2 = cursorPG.fetchone()
#print("existe2: " + str(existe2))

diam = float(datos[0][2])
zabajo = float(datos[0][5])
zarriba = float(datos[0][4])

if (datos[0][1] == 'ART'):
    espesorArriba=0.4
    espesorAbajo=0.5
    factor = 4
else:
    if (datos[0][3] > 0.7):
        espesorArriba = 0.2
    else:
        espesorArriba = 0.1
    factor = 2
    espesorAbajo = 0.3


y1 = zarriba - factor*diam - espesorAbajo
y2 = zabajo - factor*diam - espesorAbajo

y12 = diam + zarriba + factor*diam + espesorArriba
y22 = diam + zabajo + factor*diam + espesorArriba

a = datos[0][4] - datos[0][5]
b = datos[0][6]
res = b * b - (a * a)
if (res > 0):
    xf = math.sqrt(res)


def rotate_x(angle):
    c = math.cos(angle)
    s = math.sin(angle)
    return [[1, 0, 0],
            [0, c, -s],
            [0, s, c]]

def rotate_y(angle):
    c = math.cos(angle)
    s = math.sin(angle)
    return [[c, 0, s],
            [0, 1, 0],
            [-s, 0, c]]

def rotate_z(angle):
    c = math.cos(angle)
    s = math.sin(angle)
    return [[c, -s, 0],
    [s, c, 0],
    [0, 0, 1]]



#DIBUJA COTA DE TERRENO
#points = [(cotaInicial[0][0], cotaInicial[0][0], cotaInicial[0][1]), (cotaFinal[0][0], cotaFinal[0][0] + datos[0][6], cotaFinal[0][1]), (cotaInicial[0][0] + 15, cotaInicial[0][0] + 15, cotaInicial[0][1])]
points = [(0, 0, cotaInicial[0][0]), (datos[0][6] / 2, 15, (cotaInicial[0][0] + cotaFinal[0][0]) / 2), (datos[0][6], 0, cotaFinal[0][0])]
print(str(cotaFinal))
print(str(cotaInicial))
print(str(datos))
# Obtén los vectores de dirección del plano
v1PlanoTerreno = np.array(points[1]) - np.array(points[0])
v2PlanoTerreno = np.array(points[2]) - np.array(points[0])
#normal = np.cross(v1, v2)
normalPlanoTerreno = [v1PlanoTerreno[1] * v2PlanoTerreno[2] - v1PlanoTerreno[2] * v2PlanoTerreno[1],
          v1PlanoTerreno[2] * v2PlanoTerreno[0] - v1PlanoTerreno[0] * v2PlanoTerreno[2],
          v1PlanoTerreno[0] * v2PlanoTerreno[1] - v1PlanoTerreno[1] * v2PlanoTerreno[0]
]
a, b, c = normalPlanoTerreno
d = np.dot(normalPlanoTerreno, points[0])
#print(f"{a}x {b}y {c}z {d} = 0")

# Genera una malla de puntos en el plano
X, Y = np.meshgrid(np.linspace(-5, datos[0][6] / 4, 50), np.linspace(-5, datos[0][6] / 4, 50))
Z = (d - a*X - b*Y) / c

# Crea un objeto de tipo "surface" y asigna los ejes x, y y z
plane = go.Surface(x = X, y = Y, z = Z, opacity = 0.5) 


#print(str(points))
#DIBUJA COLECTOR
#label='Limite tunelera abajo'
#plt.plot([0, xf], [y1, y2], color = 'r', marker = 'o')
#label='Limite tunelera arriba'
#plt.plot([0, xf], [y12, y22], color = 'r', marker = 'o')
 # DIBUJA TRAMO-
#plt.plot([0, xf], [zarriba+diam+espesorArriba, zabajo + diam + espesorArriba], linestyle = linestyles[0], marker = '>', color = 'b')
#plt.plot([0, xf], [zarriba-espesorAbajo, zabajo - espesorAbajo], linestyle = linestyles[0], marker = '>', color = 'b')
#print(str(zarriba+diam+espesorArriba) + " " + str(zarriba-espesorAbajo) + " " + str(zabajo + diam + espesorArriba) + " " + str( zabajo - espesorAbajo))
#print(str(((zarriba+diam+espesorArriba) - (zabajo + diam + espesorArriba)) / 1) + " " + str(xf))
#zarriba+diam+espesorArriba = y1 de tramo
#zarriba-espesorAbajo = y12 de tramo

#print(str(y1) + " " + str(y2) + " " + str(y12) + " " + str(y22))
# y1 de zona roja
# y2 de zona roja
# y12 de zona roja
# y22 de zona roja

# Crea una malla de puntos en el cilindro
RadioTramo = diam / 2
thetaTramo = np.linspace(0, 2 * np.pi, 50)
#los dos primeros parametros controlan el largo del cilindro y el tercero la cantidad de puntos para dibujarlo
zTramo = np.linspace(-datos[0][6], 0, 20)
thetaTramo, zTramo = np.meshgrid(thetaTramo, zTramo)
xTramo = RadioTramo * np.cos(thetaTramo)
yTramo = RadioTramo * np.sin(thetaTramo) 


"""# Calcula el producto punto de v1 y v2
dot_product = sum(v1[i] * v2[i] for i in range(3))

# Calcula la magnitud de v1 y v2
magnitude_v1 = math.sqrt(sum(v1[i]**2 for i in range(3)))
magnitude_v2 = math.sqrt(sum(v2[i]**2 for i in range(3)))

# Calcula el coseno del ángulo entre v1 y v2
cos_angle = dot_product / (magnitude_v1 * magnitude_v2)

# Calcula el ángulo en grados
angle = math.degrees(math.acos(cos_angle))"""

rotation_matrix = rotate_y(math.pi / 2)
x_rotatedTramo = np.dot(rotation_matrix, np.vstack((xTramo.flatten(), yTramo.flatten(), zTramo.flatten())))
x_rotatedTramo = x_rotatedTramo[0].reshape(xTramo.shape)
y_rotatedTramo = np.dot(rotation_matrix, np.vstack((xTramo.flatten(), yTramo.flatten(), zTramo.flatten())))
y_rotatedTramo = y_rotatedTramo[1].reshape(yTramo.shape)
z_rotatedTramo = np.dot(rotation_matrix, np.vstack((xTramo.flatten(), yTramo.flatten(), zTramo.flatten())))
z_rotatedTramo = z_rotatedTramo[2].reshape(zTramo.shape)
x = [1, 1, 1, 1, -1, -1, -1, -1]
y = [1, 1, -1, -1, 1, 1, -1, -1]
z = [1, -1, -1, 1, 1, -1, -1, 1]
i = [0, 0, 0, 0, 4, 4, 4, 4, 0, 0, 0, 0, 4, 4, 4, 4, 1, 2, 3, 7, 6]
j = [1, 2, 3, 7, 5, 6, 7, 1, 1, 2, 3, 7, 5, 6, 7, 1, 5, 6, 7, 5, 6]
k = [3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0]


#cylinderTramo = go.Mesh3d(x = x_rotatedTramo, y = y_rotatedTramo, z = z_rotatedTramo  + (zarriba + diam + espesorArriba), scene = 'scene1', color='blue', opacity=0.50)
cylinderTramo = go.Mesh3d(x = xTramo, y = yTramo, z = zTramo, scene = 'scene1', color='blue', opacity=0.50)


#cylinder = go.Surface(x = xTramo + datos[0][6], y = yTramo  + (datos[0][6] / 2), z = zTramo + (zarriba + diam + espesorArriba))
# Añade las figuras al gráfico de Plotly
#fig = go.Figure(data = [ cylinderTramo, go.Scatter3d(x=[p[0] for p in points], y=[p[1] for p in points], z=[p[2] for p in points])])

# Creamos los vértices del cilindro
# Define el radio y la altura del cilindro
cube =  go.Mesh3d(x=x, y=y, z=z, i=i, j=j, k=k)
print(str(cube))
fig = go.Figure(data=[cylinderTramo, cube])
fig.write_html("grafico.html")




