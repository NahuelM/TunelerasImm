
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.offline as off
from dash import Dash, dcc, html, Input, Output, ctx
import psycopg2
from psycopg2.extensions import AsIs
import math
import numpy as np
from scipy.spatial import HalfspaceIntersection, Delaunay
from flask import send_from_directory
import os



def updateGraph(idTramo, diametroTunelera, profundidadTunelera, disEsquina, idEsquina):
    connectPG = psycopg2.connect("dbname=PGSEPS user=postgres password=eps host=10.60.0.245")            
    cursorPG = connectPG.cursor()
    #idTramo = "100"
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
   # print("cotaFinal: " + str(cotaFinal))
    # punto final
    cursorPG.execute("""SELECT cota, id FROM "SS_Puntos" p WHERE CAST((SELECT ST_X(ST_GeometryN(p.geom,1))) AS numeric) = 
                    (SELECT CAST((SELECT ST_X(ST_EndPoint(ST_GeometryN(t.geom,1)))) AS numeric) FROM "SS_Tramos" t WHERE CAST(id AS character varying) = '%s');""", (AsIs(idTramo),))
    existe2 = cursorPG.fetchone()
    
    if (existe1 == None or existe2 == None):
        print('Error al mostrar perfil: Datos de terreno incoherentes.')
    else:
        puntoInicial = cotaInicial[0][1]
        puntoFinal = cotaFinal[0][1]
        if (idEsquina != 0 ):
            cursorPG.execute("""SELECT ST_Distance(ST_GeometryN(t.geom,1),ST_GeometryN(p.geom,1)) from "SS_Puntos" p join "Cruces_Calles" t on cast(p.id as character varying) = '%s'
                            and cast(t.id as character varying) = '%s';""",
                            (AsIs(puntoInicial), AsIs(idEsquina)))
            distanciaInicial = cursorPG.fetchall()


            cursorPG.execute("""SELECT ST_Distance(ST_GeometryN(t.geom,1),ST_GeometryN(p.geom,1)) from "SS_Puntos" p join "Cruces_Calles" t on cast(p.id as character varying) = '%s'
                            and cast(t.id as character varying) = '%s';""",
                            (AsIs(puntoFinal), AsIs(idEsquina)))
            distanciaFinal = cursorPG.fetchall()
            #print(str(distanciaFinal))
            #print(str(distanciaInicial))
            if (distanciaFinal == None or distanciaInicial == None):
                print('Error al mostrar perfil: Datos de esquina incoherentes.')
        
        connectPG.commit()
    #print("existe2: " + str(existe2))

    #DATOS TEMPORALES AL NO TENER BASE DE DATOS
    # cotaInicial = [[45]]
    # datos = [[1, 'ART', .7, 1, 15, 20, 10]]
    # cotaFinal = [[49]]
    # distanciaEsq = disEsquina
    distanciaInicial = [[4]]
    distanciaFinal = [[1]]


    #print(str(idTramo) + " " + str(datos))
    diam = float(datos[0][2])
    zabajo = float(datos[0][5])
    zarriba = float(datos[0][4])

    colorColectorHex = '#808080'
    colorColectorRgba = 'rgba(128, 128, 128, .5)'

    if (datos[0][1] == 'ART'):
        espesorArriba = 0.4
        espesorAbajo = 0.5
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


    def rotate_xMatriz(angle):
        c = math.cos(angle)
        s = math.sin(angle)
        return [[1, 0, 0],
                [0, c, -s],
                [0, s, c]]

    def rotate_yMatriz(angle):
        c = math.cos(angle)
        s = math.sin(angle)
        return [[c, 0, s],
                [0, 1, 0],
                [-s, 0, c]]

    def rotate_zMatriz(angle):
        c = math.cos(angle)
        s = math.sin(angle)
        return [[c, -s, 0],
                [s, c, 0],
                [0, 0, 1]]

    def crearPlano(puntosArray):
        v1Plano = np.array(puntosArray[1]) - np.array(puntosArray[0])
        v2Plano = np.array(puntosArray[2]) - np.array(puntosArray[0])
        #normal = np.cross(v1, v2)
        normalPlano = [v1Plano[1] * v2Plano[2] - v1Plano[2] * v2Plano[1],
                       v1Plano[2] * v2Plano[0] - v1Plano[0] * v2Plano[2],
                       v1Plano[0] * v2Plano[1] - v1Plano[1] * v2Plano[0]
                      ]
        a, b, c = normalPlano
        d = np.dot(normalPlano, puntosArray[0])
        #print(f"{a}x {b}y {c}z {d} = 0")

        # Genera una malla de puntos en el plano
        X, Y = np.meshgrid(np.linspace(0, datos[0][6], 10), np.linspace(-3, 3, 10))
        Z = (d - a*X - b*Y) / c
        return X, Y, Z

    # Coordenadas del centro de la circunferencia
    x1 = ((zarriba + diam + espesorArriba) + (zarriba - espesorAbajo)) / 2 #Las coordenadas en x pasan a ser la altura al rotar los objectos, ya que rotan en local y sus ejes tambien rotan
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

    n = 31
    # Radios de las circunferencia
    r1 = (zarriba + diam + espesorArriba) - x1
    r2 = (zabajo + diam + espesorArriba) - x2
    r3 = yRedZone1 - x3
    r4 = yRedZone2 - x4

    ###################################    ######################################################################################################
    # FUNCION PARA CREAR CILINDROS 3D #    #RETORNA UNA MESH3D DEL CILINDRO Y DOS MATRICES CON LAS COORDS DE LAS CIRCUNFERENECIAS QUE LO FORMAN #
    ###################################    ######################################################################################################
    def crearCilindroMesh3d(XcoordC1, YcoordC1, ZCoordC1, XcoordC2, YcoordC2, ZcoordC2, radioC1, radioC2, color, opacity, info, eje, angle, name, trunco:bool):
        x_c1 = [XcoordC1 + radioC1*np.cos(t) for t in np.linspace(0, 2*np.pi, n)]
        y_c1 = [YcoordC1 + radioC1*np.sin(t) for t in np.linspace(0, 2*np.pi, n)]
        z_c1 = [ZCoordC1 for t in np.linspace(0, 2*np.pi, n)]

        x_c2 = [XcoordC2 + radioC2*np.cos(t) for t in np.linspace(0, 2*np.pi, n)]
        y_c2 = [YcoordC2 + radioC2*np.sin(t) for t in np.linspace(0, 2*np.pi, n)]
        z_c2 = [ZcoordC2 for t in np.linspace(0, 2*np.pi, n)]
        

                
        #Roto las circunferencias 
        if(eje == 'y'):
            rotation_matrix = rotate_yMatriz(angle)
        else:
            rotation_matrix = rotate_xMatriz(angle)
            
        matrizC1 = list(zip(x_c1, y_c1, z_c1))
        matrizC1 = [list(t) for t in matrizC1]

        matrizC2 = list(zip(x_c2, y_c2, z_c2))
        matrizC2 = [list(t) for t in matrizC2]
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
            
            
        ####################################################################################
        # TRUNCO RED ZONE A COTA DE TERRENO, PARA QUE LA ZONA ROJA NO SOBREPASE EL TERRENO #
        ####################################################################################
        if(trunco):
            for i in range(0, len(z_rc1)):
                if(z_rc1[i] > cotaInicial[0][0]):
                    z_rc1[i] = z_rc1[i] - (z_rc1[i] - cotaInicial[0][0])
                    print('punto por encima de terreno c1')
            
            for i in range(0, len(z_rc2)):
                if(z_rc2[i] > cotaFinal[0][0]):
                    z_rc2[i] = z_rc2[i] - (z_rc2[i] - cotaFinal[0][0])
                    print('punto por encima de terreno c2')
        # Coordenadas de los vértices
        xcy1 = []
        ycy1 = []
        zcy1 = []

        for k in range(0, n, 1):
            xcy1 = xcy1 + [x_rc1[k], x_rc2[k]]
            ycy1 = ycy1 + [y_rc1[k], y_rc2[k]]
            zcy1 = zcy1 + [z_rc1[k], z_rc2[k]]

        ViCy1 = []
        VjCy1 = []
        VkCy1 = []

        for i in range((n*2) - 2):
            ViCy1.append(i % ((n*2) - 1))
            VjCy1.append((i+1) % ((n*2) - 2))
            VkCy1.append(((i+1) % ((n*2) - 2)) + 1)
            
        # Crear una malla de la caras laterales del cilindro
        return [go.Mesh3d(x = xcy1, y = ycy1, z = zcy1, i = ViCy1, j = VjCy1, k = VkCy1, color = color, opacity = opacity, flatshading = True, intensitymode = 'cell', hovertemplate=info, name = name), [x_rc1, y_rc1, z_rc1], [x_rc2, y_rc2, z_rc2]]

    
    ladosCilindroTramo = crearCilindroMesh3d(x1, y1, z1, x2, y2, z2, r1, r2, '#b5b5b5', 1, 'Colector', 'y', math.pi / 2, name = 'ladoTramo1', trunco = False)
    ladosCilindroTramo1 = crearCilindroMesh3d(x1, y1, z1, x2, y2, z2, r1 - .1, r2 - .1, '#b5b5b5', 1, 'Colector', 'y', math.pi / 2, name = 'ladoTramo2', trunco = False)
    ladosCilindroRedZone = crearCilindroMesh3d(x3, y3, z3, x4, y4, z4, r3, r4, '#ff4255', .25, 'Zona no permitida para perforaciones', 'y', math.pi / 2, name = 'ladoRD', trunco = True)
    
    delineadoTramoC1 = go.Scatter3d(x = ladosCilindroTramo[1][0], y = ladosCilindroTramo[1][1], z = ladosCilindroTramo[1][2], mode = 'lines', marker = dict(color = 'gray'))
    delineadoTramoC2 = go.Scatter3d(x = ladosCilindroTramo[2][0], y = ladosCilindroTramo[2][1], z = ladosCilindroTramo[2][2], mode = 'lines', marker = dict(color = 'gray'))
    
    delineadoTramo1C1 = go.Scatter3d(x = ladosCilindroTramo1[1][0], y = ladosCilindroTramo1[1][1], z = ladosCilindroTramo1[1][2], mode = 'lines', marker = dict(color = 'gray'))
    delineadoTramo1C2 = go.Scatter3d(x = ladosCilindroTramo1[2][0], y = ladosCilindroTramo1[2][1], z = ladosCilindroTramo1[2][2], mode = 'lines', marker = dict(color = 'gray'))
    
    delineadoRedZoneC1 = go.Scatter3d(x = ladosCilindroRedZone[1][0], y = ladosCilindroRedZone[1][1], z = ladosCilindroRedZone[1][2], mode = 'lines', marker = dict(color = '#b50018'))
    delineadoRedZoneC2 = go.Scatter3d(x = ladosCilindroRedZone[2][0], y = ladosCilindroRedZone[2][1], z = ladosCilindroRedZone[2][2], mode = 'lines', marker = dict(color = '#b50018'))
    #propuesta tunelera más abajo
    puntosPropuestaTuneleraAbajo = [(0, 0, cotaInicial[0][0]-(profundidadTunelera+0.5*diametroTunelera)), 
                                    (datos[0][6] / 2, 15, ((cotaInicial[0][0]-(profundidadTunelera+0.5*diametroTunelera) + cotaFinal[0][0]-(profundidadTunelera+0.5*diametroTunelera))/2)), 
                                    (datos[0][6], 0, cotaFinal[0][0]-(profundidadTunelera+0.5*diametroTunelera))
                                    ]

    #propuesta tunelera más arriba
    puntosPropuestaTuneleraArriba = [(0, 0, cotaInicial[0][0]-(profundidadTunelera-0.5*diametroTunelera)), 
                                    (datos[0][6] / 2, 15, ((cotaInicial[0][0]-(profundidadTunelera-0.5*diametroTunelera) + cotaFinal[0][0]-(profundidadTunelera-0.5*diametroTunelera))/2)), 
                                    (datos[0][6], 0, cotaFinal[0][0]-(profundidadTunelera-0.5*diametroTunelera))
                                    ]
    #DIBUJA COTA DE TERRENO
    puntosPlanoTerreno = [(0, 0, cotaInicial[0][0]), 
                        (datos[0][6] / 2, 15, (cotaInicial[0][0] + cotaFinal[0][0]) / 2), 
                        (datos[0][6], 0, cotaFinal[0][0])
                        ]
    lado = 2*(puntosPlanoTerreno[2][2] - (yRedZone22 + 2*r4))

    def crearPlanoMesh3d(puntosPlano, color, opcacity, info):
        #Creo los 4 vertices del cuadrado que representan una porcion del plano que pasa por los puntos que definen al mismo 
        vertcicesPlanoArray = [(puntosPlano[0][0], puntosPlano[0][1] + (lado/2), puntosPlano[0][2]),
                               (puntosPlano[2][0], puntosPlano[2][1] + (lado/2), puntosPlano[2][2]),
                               (puntosPlano[0][0], puntosPlano[0][1] - (lado/2), puntosPlano[0][2]),
                               (puntosPlano[2][0], puntosPlano[2][1] - (lado/2), puntosPlano[2][2])
                              ]
        x = [v[0] for v in vertcicesPlanoArray]
        y = [v[1] for v in vertcicesPlanoArray]
        z = [v[2] for v in vertcicesPlanoArray]
        i = [0, 2]
        j = [1, 3]
        k = [2, 1]
        return go.Mesh3d(x=x, y=y, z=z, i=i, j=j, k=k, color=color, opacity=opcacity, lighting = dict(
            ambient = 0.5,
            diffuse = .1,
            specular = .5,
            roughness = 0.5,
            fresnel = .1,
            vertexnormalsepsilon = 1e-20,
            facenormalsepsilon = 0
        ), 
        lightposition = dict(x = 0, y = 0, z = 10000),
        intensitymode = 'cell',
        flatshading = True,
        hovertemplate=info)

    ###########################################
    # FUNCION PARA CREAR PARALEPIPEDOS RECTOS #
    ###########################################
    def crearCubeMesh3d(puntosPlano, color, opcacity, info, extrudeDistance):
        #Creo los 4 vertices del cuadrado que representan una porcion del plano que pasa por los puntos que definen al mismo 
        vertcicesPlanoArray = [(puntosPlano[0][0], puntosPlano[0][1] + (lado/2), puntosPlano[0][2]),
                               (puntosPlano[2][0], puntosPlano[2][1] + (lado/2), puntosPlano[2][2]),
                               (puntosPlano[0][0], puntosPlano[0][1] - (lado/2), puntosPlano[0][2]),
                               (puntosPlano[2][0], puntosPlano[2][1] - (lado/2), puntosPlano[2][2]),
                               (puntosPlano[0][0], puntosPlano[0][1] + (lado/2), puntosPlano[0][2] + extrudeDistance),
                               (puntosPlano[2][0], puntosPlano[2][1] + (lado/2), puntosPlano[2][2] + extrudeDistance),
                               (puntosPlano[0][0], puntosPlano[0][1] - (lado/2), puntosPlano[0][2] + extrudeDistance),
                               (puntosPlano[2][0], puntosPlano[2][1] - (lado/2), puntosPlano[2][2] + extrudeDistance)
                              ]
        x = [v[0] for v in vertcicesPlanoArray]
        y = [v[1] for v in vertcicesPlanoArray]
        z = [v[2] for v in vertcicesPlanoArray]
        i = [0, 2, 4, 6, 0, 4, 1, 7, 3, 2, 2, 4]
        j = [1, 3, 5, 7, 4, 5, 3, 3, 7, 6, 6, 0]
        k = [2, 1, 6, 5, 1, 1, 5, 5, 2, 7, 0, 6]
        return go.Mesh3d(x=x, y=y, z=z, i=i, j=j, k=k, color=color, opacity=opcacity, 
        lightposition = dict(x = 1000, y = 0, z = 10000),
        intensitymode = 'cell',
        flatshading = True,
        hovertemplate=info
        )

    cilindroTunelera = None
    borderCilindroTun1 = None
    borderCilindroTun = None
    trayectoriaTun = None
    if (idEsquina != 0):
        if (distanciaFinal[0][0] < distanciaInicial[0][0]):
            xDisEsquina = distanciaInicial[0][0] - disEsquina
        else:
            xDisEsquina = disEsquina - distanciaInicial[0][0]

        profundidadReltaiva = cotaInicial[0][0] - (profundidadTunelera/2 + diametroTunelera/2)
        cilindroTunelera = crearCilindroMesh3d(xDisEsquina, -profundidadReltaiva, lado/1.5, xDisEsquina, -profundidadReltaiva, -lado/1.5, diametroTunelera/2, diametroTunelera/2, 'rgba(204, 204, 204, .15)', 1, 'Tunelera', 'x', math.pi / 2, name='propTun', trunco = False)
        borderCilindroTun = go.Scatter3d(x = cilindroTunelera[1][0], y = cilindroTunelera[1][1], z = cilindroTunelera[1][2], mode = 'lines', marker = dict(color = 'black'))
        borderCilindroTun1 = go.Scatter3d(x = cilindroTunelera[2][0], y = cilindroTunelera[2][1], z = cilindroTunelera[2][2], mode = 'lines', marker = dict(color = 'black'))
        trayectoriaTun = go.Scatter3d(x = [xDisEsquina, xDisEsquina], y = [lado/1.5, -lado/1.5], z = [profundidadReltaiva, profundidadReltaiva], mode='lines+markers',  marker = dict(color = 'black', size = 5), line=dict(dash = 'longdashdot'))
    
        
    cantFrames = 35
    yFrames = np.linspace(-lado/1.5, lado/1.5, cantFrames)
    framesAnim = [go.Frame(data=[go.Scatter3d(x = [xDisEsquina], y = [yFrames[k]], z = [profundidadReltaiva], mode = 'markers', marker=dict(color="red", size=10))]) for k in range(cantFrames)]
    
    anotaciones3D = go.Scatter3d(x = [xf, 0, xf / 2],
                                 y = [y2, y1, y1], 
                                 z = [x2 - r4 + .1, x1 - r3 + .1, (x2 - r4 + .1 + x1 - r3 + .1 )/2], 
                                 text = ['◄', '►', 'largo de colector: '+ str(round(xf, 2)) + 'm'], 
                                 mode = 'lines+text', 
                                 textposition='middle center', 
                                 line=dict(color= 'rgb(70,70,70)', width=2))

    linesAnotaciones1 = go.Scatter3d(x = [puntosPlanoTerreno[0][0], z3, puntosPlanoTerreno[0][0]], 
                                     y = [puntosPlanoTerreno[0][1], y3, puntosPlanoTerreno[0][1]],
                                     z = [puntosPlanoTerreno[0][2], x3 - r3, (puntosPlanoTerreno[0][2] + ( x3 - r3))/2],
                                     mode = 'lines+text',
                                     text = ['▲', '▼', 'Distancia de terreno a zona prohibida para perforar: ' + str(round(puntosPlanoTerreno[0][2] - ( x3 - r3), 2)) + "m"],
                                     textposition = 'middle center',
                                     line = dict(color= 'rgb(70,70,70)', width=2))

    linesAnotaciones2 = go.Scatter3d(x = [puntosPlanoTerreno[2][0], xf, puntosPlanoTerreno[2][0]], 
                                     y = [puntosPlanoTerreno[2][1], y4, puntosPlanoTerreno[2][1]],
                                     z = [puntosPlanoTerreno[2][2], x4 - r4, (puntosPlanoTerreno[2][2] + ( x4 - r4))/2],
                                     mode = 'lines+text',
                                     text = ['▲', '▼', 'Distancia de terreno a zona prohibida para perforar: ' + str(round(puntosPlanoTerreno[2][2] - ( x4 - r4), 2)) + "m"],
                                     textposition = 'middle center',
                                     line = dict(color= 'rgb(70,70,70)', width=2))

    linesAnotaciones3 = go.Scatter3d(x = [xf / 2, xf / 2, xf/2], 
                                     y = [0, 0, 0],
                                     z = [puntosPlanoTerreno[1][2], puntosPropuestaTuneleraArriba[1][2], (puntosPlanoTerreno[1][2] + puntosPropuestaTuneleraArriba[1][2])/2],
                                     mode = 'lines+text',
                                     text = ['▲', '▼', str(round(puntosPlanoTerreno[1][2] - puntosPropuestaTuneleraArriba[1][2],2)) + "m"],
                                     textposition = 'middle center',
                                     line = dict(color= 'rgb(70,70,70)', width=2))

    offset = puntosPlanoTerreno[2][2] - (yRedZone22 + 2*r4) + .5

    linesBorder1 = go.Scatter3d(x = [puntosPlanoTerreno[0][0], puntosPlanoTerreno[0][0], puntosPlanoTerreno[2][0], puntosPlanoTerreno[2][0]], 
                                y = [puntosPlanoTerreno[0][1] + (lado/2), puntosPlanoTerreno[0][1] + (lado/2),  puntosPlanoTerreno[2][1] + (lado/2), puntosPlanoTerreno[2][1] + (lado/2)],
                                z = [puntosPlanoTerreno[0][2], puntosPlanoTerreno[0][2] - offset, puntosPlanoTerreno[2][2] - offset, puntosPlanoTerreno[2][2] ],
                                mode = 'lines',
                                line = dict(color= 'rgb(70,70,70)', width = 3))

    linesBorder2 = go.Scatter3d(x = [puntosPlanoTerreno[2][0], puntosPlanoTerreno[2][0], puntosPlanoTerreno[2][0]], 
                                y = [puntosPlanoTerreno[2][1] + (lado/2), puntosPlanoTerreno[2][1] - (lado/2), puntosPlanoTerreno[2][1] - (lado/2)],
                                z = [ puntosPlanoTerreno[2][2] - offset, puntosPlanoTerreno[2][2] - offset, puntosPlanoTerreno[2][2]],
                                mode = 'lines',
                                line = dict(color= 'rgb(70,70,70)', width = 3))

    linesBorder3 = go.Scatter3d(x = [ puntosPlanoTerreno[2][0] , puntosPlanoTerreno[0][0], puntosPlanoTerreno[0][0]], 
                                y = [puntosPlanoTerreno[2][1] - (lado/2), puntosPlanoTerreno[0][1] - (lado/2), puntosPlanoTerreno[0][1] - (lado/2)],
                                z = [puntosPlanoTerreno[2][2] - offset , puntosPlanoTerreno[0][2] - offset, puntosPlanoTerreno[0][2]],
                                mode = 'lines',
                                line = dict(color= 'rgb(70,70,70)', width = 3))

    linesBorder4 = go.Scatter3d(x = [puntosPlanoTerreno[0][0], puntosPlanoTerreno[0][0]], 
                                y = [ puntosPlanoTerreno[0][1] - (lado/2), puntosPlanoTerreno[0][1] + (lado/2)],
                                z = [puntosPlanoTerreno[0][2] - offset, puntosPlanoTerreno[0][2] - offset],
                                mode = 'lines',
                                line = dict(color= 'rgb(70,70,70)', width = 3))

    xAux = ladosCilindroTramo[0].x + ladosCilindroTramo1[0].x
    yAux = ladosCilindroTramo[0].y + ladosCilindroTramo1[0].y
    zAux = ladosCilindroTramo[0].z + ladosCilindroTramo1[0].z

    iAux = np.concatenate((np.array(np.linspace(0, (n*2)-2, n)), np.array(np.linspace(1, (n*2)-1, n))))
    jAux = np.concatenate((np.array(np.linspace((n*2), (n*4)-2, n)), np.array(np.linspace((n*2)+1, (n*4)-1, n))))
    kAux = np.concatenate((np.array(np.linspace(2, (n*2), n)), np.array(np.linspace(3, (n*2)+1, n))))

    iAux1 = np.concatenate((np.linspace((n*2)+1, (n*4)-3, n-1), np.linspace((n*2), (n*4)-4, n-1)))#[62, 64, 66, 68]
    jAux1 = np.concatenate((np.linspace(3, (n*2)-1, n-1), np.linspace(2, (n*2)-2, n-1))) #[2, 4, 6, 8]
    kAux1 = np.concatenate((np.linspace((n*2)+3, (n*4)-1, n-1), np.linspace((n*2)+2, (n*4)-2, n-1))) #[64, 66, 68, 70]

    frenteColector = go.Mesh3d(x=xAux, y=yAux, z=zAux, i = np.concatenate((iAux1, iAux)), j = np.concatenate((jAux1, jAux)), k = np.concatenate((kAux1, kAux)), color = '#b5b5b5', opacity = 1, flatshading = True, intensitymode = 'cell', hovertemplate='Colector')

    #crearCubeMesh3d(puntosPropuestaTuneleraArriba, '#42ff4f', .2, 'zona para perforar segun parametros ingresados', -diametroTunelera)
    
    fig = go.Figure(data = [ladosCilindroTramo[0], ladosCilindroTramo1[0], ladosCilindroRedZone[0], crearCubeMesh3d(puntosPlanoTerreno, '#808080', 1, 'Superficie', .12),
                            linesBorder1, linesBorder2, linesBorder3, linesBorder4, frenteColector, 
                            delineadoTramoC1, delineadoTramoC2, delineadoTramo1C1, delineadoTramo1C2, delineadoRedZoneC1, delineadoRedZoneC2, borderCilindroTun, borderCilindroTun1, trayectoriaTun, cilindroTunelera[0]], 
                            frames=framesAnim, 
                            layout = go.Layout(updatemenus=[dict(
                                        type = "buttons",
                                        buttons = [dict(label = "Play",
                                        method = "animate",
                                        args = [None, dict(frame=dict(duration=10))])])],
                                               scene_camera = dict(eye=dict(x=-xDisEsquina, y=.5, z=.1), center = dict(x = -xDisEsquina/2, y = 0, z = -.2)))
                    )
    

    fig.update_layout(
        scene_xaxis_visible=False,
        scene_yaxis_visible=False,
        scene_zaxis_visible=False,
        showlegend = False,
        scene = dict(annotations = [dict(x = xf, 
                                    y = 0, 
                                    z = cotaInicial[0][0], 
                                    text = 'Largo de colector: '+str(round(xf, 2)) + 'm' + '<br>Aguas arriba', 
                                    arrowcolor = "black",
                                    arrowsize = 2,
                                    arrowwidth = 1,
                                    arrowhead = 1,
                                    xanchor = 'left',
                                    bordercolor = '#969696', bgcolor = '#cccccc', align = 'left'
                                    ),
                                    dict(x = xDisEsquina, y = -lado/1.5, z = cotaInicial[0][0] - profundidadTunelera, text = 'Camino para tunelera<br>Profundidad' + str(profundidadTunelera) + 'm' + '<br>Diametro: ' + str(diametroTunelera) + 'm',
                                         bordercolor = '#969696', bgcolor = '#cccccc', align = 'left' )],
                     aspectmode='data',
                     ),
        # scene_camera = dict(
        #     eye=dict(x=2, y=2, z=0.1)
        #)
    )
    fig.layout.height = 1080
    fig.write_html("grafico.html")

    def crear2D():
        #COTA DE TERRENO
        terreno = go.Scatter(x = [0, xf], y = [cotaInicial[0][0], cotaFinal[0][0]],  marker = dict(color = 'gray'), mode = 'lines')
        
        # DIBUJA TRAMO
        tramoArriba = go.Scatter(x = [0, xf], y = [zarriba+diam+espesorArriba, zabajo+diam+espesorArriba], legendgroup = 'tramo',  marker = dict(color = colorColectorHex), mode = 'lines')
        tramoAbajo =  go.Scatter(x = [0, xf], y = [zarriba-espesorAbajo, zabajo-espesorAbajo], legendgroup = 'tramo',  marker = dict(color = colorColectorHex), mode = 'lines')
        

        #RED ZONE
        limRedZoneAbajo = go.Scatter(x = [0, xf], y = [yRedZone1, yRedZone2], legendgroup = 'redZone', marker = dict(color = '#ff4255'), mode = 'lines')
        limRedZoneArriba = go.Scatter(x = [0, xf], y = [yRedZone12, yRedZone22], legendgroup = 'redZone', marker = dict(color = '#ff4255'), mode = 'lines')

        #PROPUESTA TUNELERA
        propTunArriba = go.Scatter(x = [0, xf], y = [cotaInicial[0][0] - (profundidadTunelera + 0.5*diametroTunelera), cotaFinal[0][0] - (profundidadTunelera + 0.5*diametroTunelera)], legendgroup = 'propTun',  marker = dict(color = 'green'), line = dict(dash = 'dash'), mode = 'lines') 
        propTunAbajo = go.Scatter(x = [0, xf], y = [cotaInicial[0][0] - (profundidadTunelera - 0.5*diametroTunelera), cotaFinal[0][0] - (profundidadTunelera - 0.5*diametroTunelera)], legendgroup = 'propTun',  marker = dict(color = 'green'), line = dict(dash = 'dash'), mode = 'lines')
        
        #FILL
        x = [0, xf, xf, 0]
        y = [zarriba+diam+espesorArriba, zabajo+diam+espesorArriba, zabajo-espesorAbajo, zarriba-espesorAbajo]
        fillTramoArea = go.Scatter(x = x, y = y, mode = 'none', legendgroup = 'tramo', fill = 'toself', fillcolor = colorColectorRgba, showlegend = False)

        y = [zarriba - espesorAbajo, zabajo - espesorAbajo, yRedZone2, yRedZone1]
        fillRedZoneArriba = go.Scatter(x = x, y = y, mode = 'none', legendgroup = 'redZone', fill = 'toself', fillcolor = 'rgba(255, 66, 85, .5)', showlegend = False)
        y = [yRedZone12, yRedZone22, zabajo + diam + espesorArriba, zarriba + diam + espesorArriba]
        fillRedZoneAbajo = go.Scatter(x = x, y = y, mode = 'none', legendgroup = 'redZone', fill = 'toself', fillcolor = 'rgba(255, 66, 85, .5)', showlegend = False)
        
        coordsCenterTuneleras = [xDisEsquina, 0,  cotaInicial[0][0] - (profundidadTunelera)]
        puntosAux = go.Scatter(x = [coordsCenterTuneleras[0]-diametroTunelera/2, coordsCenterTuneleras[0]+diametroTunelera/2], y = [coordsCenterTuneleras[2]-diametroTunelera/2, coordsCenterTuneleras[2]+diametroTunelera/2])

        fig = go.Figure(data=([terreno, tramoArriba, tramoAbajo, limRedZoneAbajo, limRedZoneArriba, propTunArriba, propTunAbajo, fillTramoArea, fillRedZoneArriba, fillRedZoneAbajo]))
        
        #Dibuja un circulo inscripto en el cuadrado con el vertice inferior izquiero en coords(x0, y0) y el vertice superior derecho (x1, y1)
        fig.add_shape(type="circle",
            xref="x", yref="y",
            x0 = coordsCenterTuneleras[0]-diametroTunelera/2, y0 = coordsCenterTuneleras[2]-diametroTunelera/2, x1 = coordsCenterTuneleras[0]+diametroTunelera/2, y1 = coordsCenterTuneleras[2]+diametroTunelera/2,
            line_color="black",
        )
        fig.update_layout(scene_xaxis_visible = False, scene_yaxis_visible = False, scene = dict(aspectmode = 'data'))
        return fig

    return [fig, crear2D()]

external_stylesheets = [
    {
        'href': 'static/styles.css',
        'rel': 'stylesheet'
    }
]



app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div([
    html.Div([html.Label('id de Tramo',className='label'),
            dcc.Input(value = '1', type = 'number', id = 'idT', className='Input'),
            html.Label('Diametro tunelera', className='label'),
            dcc.Input(value = '0', type = 'number', id = 'diametroTun', className='Input'),
            html.Label('Profundidad Tunelera', className='label'),
            dcc.Input(value = '0', type = 'number', id = 'profundidadTun', className='Input'),
            html.Label('distancia a Esquina', className='label'),
            dcc.Input(value = '1', type = 'number', id = 'disEsq', className='Input'),
            html.Label('id Esquina', className='label'),
            dcc.Input(value = '0', type = 'number', id = 'idDT', className='Input'),
            html.Button('Gnerear grafico', id='button', n_clicks = 0, className='Button')
            ], id = 'InputLabel'),
   
    
    html.Div([
              dcc.Graph(figure = updateGraph(1, 0, 0, disEsquina = 0, idEsquina = 1)[0], id = 'graph3D'),
              dcc.Graph(figure = updateGraph(1, 0, 0, disEsquina = 0, idEsquina = 1)[1], id = 'graph2D')
             ],
             id = 'Graficos')
], id = 'MainLabel')

#app.css.append_css({"external_url":"static/styles.css"})

@app.callback(
    Output('graph3D', 'figure'),
    Output('graph2D', 'figure'),
    Input('idT', 'value'),
    Input('diametroTun', 'value'),
    Input('profundidadTun', 'value'),
    Input('disEsq', 'value'),
    Input('idDT', 'value'),
    Input('button', 'n_clicks'),
)
def update_figure(selectedID, diametroTunelera, profundidadTunelera, disEsquina, idEsq, n_clicks):
    if 'button' == ctx.triggered_id:
        fig = updateGraph(selectedID, float(diametroTunelera), float(profundidadTunelera), float(disEsquina), idEsq)
        fig[0].update_layout(transition_duration = 1000)
        fig[1].update_layout(transition_duration = 500)
    else:
        fig = updateGraph(selectedID, float(0), float(0), float(disEsquina), idEsq)
        fig[0].update_layout(transition_duration = 1000)
        fig[1].update_layout(transition_duration = 500)
    return fig

@app.server.route('/static/<path:path>')
def static_file(path):
    static_folder = os.path.join(os.getcwd(), 'static')
    return send_from_directory(static_folder, path)
if __name__ == '__main__':
    app.run_server(debug = True)




