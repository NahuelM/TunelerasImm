
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.offline as off
from dash import Dash, dcc, html, Input, Output, ctx
import psycopg2
from psycopg2.extensions import AsIs
import math
import numpy as np



def updateGraph(idTramo, diametroTunelera, profundidadTunelera):
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
    #print("cotaFinal: " + str(cotaFinal))
    # punto final
    cursorPG.execute("""SELECT cota, id FROM "SS_Puntos" p WHERE CAST((SELECT ST_X(ST_GeometryN(p.geom,1))) AS numeric) = 
                    (SELECT CAST((SELECT ST_X(ST_EndPoint(ST_GeometryN(t.geom,1)))) AS numeric) FROM "SS_Tramos" t WHERE CAST(id AS character varying) = '%s');""", (AsIs(idTramo),))
    existe2 = cursorPG.fetchone()
    #print("existe2: " + str(existe2))
    print(str(idTramo) + " " + str(datos))
    diam = float(datos[0][2])
    zabajo = float(datos[0][5])
    zarriba = float(datos[0][4])

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

    def crearCilindroMesh3d(XcoordC1, YcoordC1, ZCoordC1, XcoordC2, YcoordC2, ZcoordC2, radioC1, radioC2, color, opacity, info):
        x_c1 = [XcoordC1 + radioC1*np.cos(t) for t in np.linspace(0, 2*np.pi, n)]
        y_c1 = [YcoordC1 + radioC1*np.sin(t) for t in np.linspace(0, 2*np.pi, n)]
        z_c1 = [ZCoordC1 for t in np.linspace(0, 2*np.pi, n)]

        x_c2 = [XcoordC2 + radioC2*np.cos(t) for t in np.linspace(0, 2*np.pi, n)]
        y_c2 = [YcoordC2 + radioC2*np.sin(t) for t in np.linspace(0, 2*np.pi, n)]
        z_c2 = [ZcoordC2 for t in np.linspace(0, 2*np.pi, n)]
        #Roto las circunferencias 
        rotation_matrix = rotate_yMatriz(math.pi / 2)
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
        return go.Mesh3d(x = xcy1, y = ycy1, z = zcy1, i = ViCy1, j = VjCy1, k = VkCy1, color = color, opacity = opacity, flatshading = True, intensitymode = 'cell', hovertemplate=info)

    ladosCilindroTramo = crearCilindroMesh3d(x1, y1, z1, x2, y2, z2, r1, r2, '#b5b5b5', 1, 'Colector')
    ladosCilindroTramo1 = crearCilindroMesh3d(x1, y1, z1, x2, y2, z2, r1 - .1, r2 - .1, '#b5b5b5', 1, 'Colector')
    ladosCilindroRedZone = crearCilindroMesh3d(x3, y3, z3, x4, y4, z4, r3, r4, '#7a0004', .25, 'Zona no permitida para perforaciones')

    #diametroTunelera = .1
    #profundidadTunelera = .7

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

    anotaciones3D = go.Scatter3d(x = [xf, 0, xf / 2],
                                y = [y2, y1, y1], 
                                z = [x2 + r2 + .1, x1 + r1 + .1, (x2 + r2 + .1 + x1 + r1 + .1 )/2], 
                                text = ['◄', '►', str(xf) + 'm'], 
                                mode = 'lines+text', 
                                textposition='middle center', 
                                line=dict(color= 'rgb(70,70,70)', width=2))

    linesAnotaciones1 = go.Scatter3d(x = [puntosPlanoTerreno[0][0], z3, puntosPlanoTerreno[0][0]], 
                                    y = [puntosPlanoTerreno[0][1], y3, puntosPlanoTerreno[0][1]],
                                    z = [puntosPlanoTerreno[0][2], x3 - r3, (puntosPlanoTerreno[0][2] + ( x3 - r3))/2],
                                    mode = 'lines+text',
                                    text = ['▲', '▼', str(puntosPlanoTerreno[0][2] - ( x3 - r3)) + "m"],
                                    textposition = 'middle center',
                                    line = dict(color= 'rgb(70,70,70)', width=2))

    linesAnotaciones2 = go.Scatter3d(x = [puntosPlanoTerreno[2][0], xf, puntosPlanoTerreno[2][0]], 
                                    y = [puntosPlanoTerreno[2][1], y4, puntosPlanoTerreno[2][1]],
                                    z = [puntosPlanoTerreno[2][2], x4 - r4, (puntosPlanoTerreno[2][2] + ( x4 - r4))/2],
                                    mode = 'lines+text',
                                    text = ['▲', '▼', str(puntosPlanoTerreno[2][2] - ( x4 - r4)) + "m"],
                                    textposition = 'middle center',
                                    line = dict(color= 'rgb(70,70,70)', width=2))

    linesAnotaciones3 = go.Scatter3d(x = [xf / 2, xf / 2, xf/2], 
                                    y = [0, 0, 0],
                                    z = [puntosPlanoTerreno[1][2], puntosPropuestaTuneleraArriba[1][2], (puntosPlanoTerreno[1][2] + puntosPropuestaTuneleraArriba[1][2])/2],
                                    mode = 'lines+text',
                                    text = ['▲', '▼', str(puntosPlanoTerreno[1][2] - puntosPropuestaTuneleraArriba[1][2]) + "m"],
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

    xAux = ladosCilindroTramo.x + ladosCilindroTramo.x
    yAux = ladosCilindroTramo.y + ladosCilindroTramo1.y
    zAux = ladosCilindroTramo.z + ladosCilindroTramo1.z

    iAux = np.concatenate((np.array(np.linspace(0, (n*2)-2, n)), np.array(np.linspace(1, (n*2)-1, n))))
    jAux = np.concatenate((np.array(np.linspace((n*2), (n*4)-2, n)), np.array(np.linspace((n*2)+1, (n*4)-1, n))))
    kAux = np.concatenate((np.array(np.linspace(2, (n*2), n)), np.array(np.linspace(3, (n*2)+1, n))))

    iAux1 = np.concatenate((np.linspace((n*2)+1, (n*4)-3, n-1), np.linspace((n*2), (n*4)-4, n-1)))#[62, 64, 66, 68]
    jAux1 = np.concatenate((np.linspace(3, (n*2)-1, n-1), np.linspace(2, (n*2)-2, n-1))) #[2, 4, 6, 8]
    kAux1 = np.concatenate((np.linspace((n*2)+3, (n*4)-1, n-1), np.linspace((n*2)+2, (n*4)-2, n-1))) #[64, 66, 68, 70]

    frenteColector = go.Mesh3d(x=xAux, y=yAux, z=zAux, i = np.concatenate((iAux1, iAux)), j = np.concatenate((jAux1, jAux)), k = np.concatenate((kAux1, kAux)), color = '#b5b5b5', opacity = 1, flatshading = True, intensitymode = 'cell', hovertemplate='Colector')

    fig = go.Figure(data = [ladosCilindroTramo, ladosCilindroTramo1, ladosCilindroRedZone, crearCubeMesh3d(puntosPlanoTerreno, '#808080', 1, 'Terreno', .12),
                            anotaciones3D, linesAnotaciones1, linesAnotaciones2, linesAnotaciones3, linesBorder1, linesBorder2, linesBorder3, linesBorder4, frenteColector, crearCubeMesh3d(puntosPropuestaTuneleraArriba, '#42ff4f', .2, 'zona para perforar segun parametros ingresados', -diametroTunelera)
                        ])

    fig.update_layout(
        title = "TUNELERAS",
        scene_xaxis_visible=False,
        scene_yaxis_visible=False,
        scene_zaxis_visible=False,
        showlegend = False
    )
    fig.layout.height = 1080
    fig.write_html("grafico.html")
    return fig

app = Dash(__name__)

app.layout = html.Div([
    html.Label('id de Tramo', style = {'fontSize': 14}),
    dcc.Input(value = '1', type = 'number', id = 'idT', style = {  'width': '25%',  'padding': '12px 20px',  'margin': '8px 0', 'border-radius': '4px'}),
    html.Label('Diametro tunelera', style = {'fontSize': 14}),
    dcc.Input(value = '0', type = 'number', id = 'diametroTun', style = {  'width': '25%',  'padding': '12px 20px',  'margin': '8px 0', 'border-radius': '4px'}),
    html.Label('Profundidad Tunelera', style = {'fontSize': 14}),
    dcc.Input(value = '0', type = 'number', id = 'profundidadTun', style = {  'width': '25%',  'padding': '12px 20px',  'margin': '8px 0', 'border-radius': '4px'}),
    html.Button('Gnerear grafico', id='button', n_clicks = 0, style = {'background-color': '#04AA6D', 'border': 'none', 'color': 'white', 'padding': '16px 32px', 'text-decoration': 'none', 'margin': '4px 2px', 'cursor': 'pointer'}),
    dcc.Graph(figure = updateGraph(1, 0, 0), id = 'graph')
])
@app.callback(
    Output('graph', 'figure'),
    Input('idT', 'value'),
    Input('diametroTun', 'value'),
    Input('profundidadTun', 'value'),
    Input('button', 'n_clicks'),
)
def update_figure(selectedID, diametroTunelera, profundidadTunelera, n_clicks):
    if 'button' == ctx.triggered_id:

        fig = updateGraph(selectedID, float(diametroTunelera), float(profundidadTunelera))
        fig.layout.height = 1080
        fig.update_layout(transition_duration=500)
    else:
        fig = updateGraph(1, float(0), float(0))
        fig.layout.height = 1080
        fig.update_layout(transition_duration=500)
    return fig


if __name__ == '__main__':
    app.run_server(debug = True)




