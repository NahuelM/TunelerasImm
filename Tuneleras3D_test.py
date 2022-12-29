
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.offline as off

import psycopg2
from psycopg2.extensions import AsIs
import math
import numpy as np

connectPG = psycopg2.connect("dbname=PGSEPS user=postgres password=eps host=10.60.0.245")            
cursorPG = connectPG.cursor()
idTramo = "98"
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


yRedZone1 = zarriba - factor*diam - espesorAbajo
yRedZone2 = zabajo - factor*diam - espesorAbajo

yRedZone12 = diam + zarriba + factor*diam + espesorArriba
yRedZone22 = diam + zabajo + factor*diam + espesorArriba

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
points = [(0, 0, cotaInicial[0][0]), (datos[0][6] / 2, 15, (cotaInicial[0][0] + cotaFinal[0][0]) / 2), (datos[0][6], 0, cotaFinal[0][0])]
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
X, Y = np.meshgrid(np.linspace(0, datos[0][6], 10), np.linspace(-15, 15, 10))
Z = (d - a*X - b*Y) / c

# Crea un objeto de tipo "surface" y asigna los ejes x, y y z
plane = go.Surface(x = X, y = Y, z = Z, opacity = 0.5) 
terreno = go.Mesh3d(x = X, y=Y, z=Z, color='gray', opacity=.8)

#DIBUJA COLECTOR
#label='Limite tunelera abajo'
#plt.plot([0, xf], [y1, y2], color = 'r', marker = 'o')
#label='Limite tunelera arriba'
#plt.plot([0, xf], [y12, y22], color = 'r', marker = 'o')
 # DIBUJA TRAMO-
#plt.plot([0, xf], [zarriba+diam+espesorArriba, zabajo + diam + espesorArriba], linestyle = linestyles[0], marker = '>', color = 'b')
#plt.plot([0, xf], [zarriba-espesorAbajo, zabajo - espesorAbajo], linestyle = linestyles[0], marker = '>', color = 'b')



# Coordenadas del centro de la circunferencia
x1 = ((zarriba + diam + espesorArriba) + (zarriba - espesorAbajo))/2 #Las coordenadas en x pasan a ser la altura al rotar los objectos, ya que rotan en local y sus ejes tambien rotan
y1 = 0
z1 = 0 #Las coordenadas en z pasan a ser el eje x

x2 = ((zabajo + diam + espesorArriba) + (zabajo - espesorAbajo)) / 2
y2 = 0
z2 = -xf

x3 = (yRedZone1 + yRedZone12) / 2
y3 = 0
z3 = 0

x4 = (yRedZone2 + yRedZone22) / 2
y4 = 0
z4 = -xf

n = 101
# Radio de la circunferencia
r1 = (zarriba + diam + espesorArriba) - x1
r2 = (zabajo + diam + espesorArriba) - x2
r3 = yRedZone1 - x3
r4 = yRedZone2 - x4

x_c1 = [x1 + r1*np.cos(t) for t in np.linspace(0, 2*np.pi, n)]
y_c1 = [y1 + r1*np.sin(t) for t in np.linspace(0, 2*np.pi, n)]
z_c1 = [z1 for t in np.linspace(0, 2*np.pi, n)]

x_c2 = [x2 + r2*np.cos(t) for t in np.linspace(0, 2*np.pi, n)]
y_c2 = [y2 + r2*np.sin(t) for t in np.linspace(0, 2*np.pi, n)]
z_c2 = [z2 for t in np.linspace(0, 2*np.pi, n)]

x_c3 = [x3 + r3*np.cos(t) for t in np.linspace(0, 2*np.pi, n)]
y_c3 = [y3 + r3*np.sin(t) for t in np.linspace(0, 2*np.pi, n)]
z_c3 = [z3 for t in np.linspace(0, 2*np.pi, n)]

x_c4 = [x4 + r4*np.cos(t) for t in np.linspace(0, 2*np.pi, n)]
y_c4 = [y4 + r4*np.sin(t) for t in np.linspace(0, 2*np.pi, n)]
z_c4 = [z4 for t in np.linspace(0, 2*np.pi, n)]


rotation_matrix = rotate_y(math.pi / 2)
matrizC1 = list(zip(x_c1, y_c1, z_c1))
matrizC1 = [list(t) for t in matrizC1]

matrizC2 = list(zip(x_c2, y_c2, z_c2))
matrizC2 = [list(t) for t in matrizC2]

matrizC3 = list(zip(x_c3, y_c3, z_c3))
matrizC3 = [list(t) for t in matrizC3]

matrizC4 = list(zip(x_c4, y_c4, z_c4))
matrizC4 = [list(t) for t in matrizC4]

x_rc1 = []
y_rc1 = []
z_rc1 = []

for row in matrizC1:
    rotated = np.dot(row, rotation_matrix)
    x_rc1.append(rotated[0])
    y_rc1.append(rotated[1])
    z_rc1.append(rotated[2])

x_rc2 = []
y_rc2 = []
z_rc2 = []

for row in matrizC2:
    rotated = np.dot(row, rotation_matrix)
    x_rc2.append(rotated[0])
    y_rc2.append(rotated[1])
    z_rc2.append(rotated[2])

x_rc3 = []
y_rc3 = []
z_rc3 = []

for row in matrizC3:
    rotated = np.dot(row, rotation_matrix)
    x_rc3.append(rotated[0])
    y_rc3.append(rotated[1])
    z_rc3.append(rotated[2])    

x_rc4 = []
y_rc4 = []
z_rc4 = []

for row in matrizC4:
    rotated = np.dot(row, rotation_matrix)
    x_rc4.append(rotated[0])
    y_rc4.append(rotated[1])
    z_rc4.append(rotated[2])      


# Crear una malla de la circunferencia
circunferencia1 = go.Mesh3d(x = x_rc1, y = y_rc1, z = z_rc1, color = 'blue')

circunferencia2 = go.Mesh3d(x = x_rc2, y = y_rc2, z = z_rc2, color = 'blue')      

circunferencia3 = go.Mesh3d(x = x_rc3, y = y_rc3, z = z_rc3, color = 'red')

circunferencia4 = go.Mesh3d(x = x_rc4, y = y_rc4, z = z_rc4, color = 'red')   

# Coordenadas de los vértices
xcy1 = []
ycy1 = []
zcy1 = []

for k in range(0, int(n/1), 1):
    xcy1 = xcy1 + [circunferencia1.x[k], circunferencia2.x[k]]
    ycy1 = ycy1 + [circunferencia1.y[k], circunferencia2.y[k]]
    zcy1 = zcy1 + [circunferencia1.z[k], circunferencia2.z[k]]


ViCy1 = []
VjCy1 = []
VkCy1 = []
for i in range((n*2) - 2):
  ViCy1.append(i % ((n*2) - 1))
  VjCy1.append((i+1) % ((n*2) - 2))
  VkCy1.append(((i+1) % ((n*2) - 2)) + 1)
# Crear una malla de la cara
ladosCylinder1 = go.Mesh3d(x=xcy1, y=ycy1, z=zcy1, i = ViCy1, j = VjCy1, k = VkCy1, color = 'gray', opacity = 1)

# Coordenadas de los vértices
xcy2 = []
ycy2 = []
zcy2 = []

for k in range(0, int(n/1), 1):
    xcy2 = xcy2 + [circunferencia3.x[k], circunferencia4.x[k]]
    ycy2 = ycy2 + [circunferencia3.y[k], circunferencia4.y[k]]
    zcy2 = zcy2 + [circunferencia3.z[k], circunferencia4.z[k]]


ViCy2 = []
VjCy2 = []
VkCy2 = []
for i in range((n*2) - 2):
  ViCy2.append(i % ((n*2) - 1))
  VjCy2.append((i+1) % ((n*2) - 2))
  VkCy2.append(((i+1) % ((n*2) - 2)) + 1)
# Crear una malla de la cara
ladosCylinder2 = go.Mesh3d(x=xcy2, y=ycy2, z=zcy2, i = ViCy2, j = VjCy2, k = VkCy2, color = 'red', opacity = .25)

#cylinderTramo = go.Mesh3d(x = x_rotatedTramo, y = y_rotatedTramo, z = z_rotatedTramo  + (zarriba + diam + espesorArriba), scene = 'scene1', color='blue', opacity=0.50)



fig = go.Figure(data=[ladosCylinder1, ladosCylinder2, terreno, plane])
fig.write_html("grafico.html")




