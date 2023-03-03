import pandas as pd
import pyproj
import plotly.express as px
import plotly.graph_objects as go



tramos = pd.read_csv('Datos.csv')


datos_CSV = tramos.iloc[int(28780)][0:16]
datos = [datos_CSV]

x = float(datos[0][12])
y = float(datos[0][13])

transformer = pyproj.Transformer.from_crs("EPSG:32721", "EPSG:4326")
lat, lon = transformer.transform(x, y)

data_frame =  pd.DataFrame({'id':[datos[0][0]],
                            'Tipo de tramo':[datos[0][1]],
                            'Tipo de seccion':[datos[0][2]], 
                            'zarriba':[datos[0][5]],
                            'zabajo':[datos[0][6]],
                            'lat':[lat],
                            'lon':[lon],
                            'x':[datos[0][12]],
                            'y':[datos[0][13]]})

"POINT Z (569266.4489301567 6146936.394332917 0)"
"POINT Z (569261.1835221518 6146931.785564913 0)"


x = 569261.1835221518
y = 6146931.785564913
lat, lon = transformer.transform(x, y)
nueva_fila = pd.DataFrame({'id':[datos[0][0]],
                            'Tipo de tramo':[datos[0][1]],
                            'Tipo de seccion':[datos[0][2]], 
                            'zarriba':[datos[0][5]],
                            'zabajo':[datos[0][6]],
                            'lat':[lat],
                            'lon':[lon],
                            'x':[datos[0][14]],
                            'y':[datos[0][15]]})

data_frame = pd.concat([data_frame, nueva_fila])


x = 569266.4489301567
y = 6146936.394332917
lat, lon = transformer.transform(x, y)
nueva_fila = pd.DataFrame({'id':[datos[0][0]],
                            'Tipo de tramo':[datos[0][1]],
                            'Tipo de seccion':[datos[0][2]], 
                            'zarriba':[datos[0][5]],
                            'zabajo':[datos[0][6]],
                            'lat':[lat],
                            'lon':[lon],
                            'x':[datos[0][14]],
                            'y':[datos[0][15]]})

data_frame = pd.concat([data_frame, nueva_fila])


x = float(datos[0][14])
y = float(datos[0][15])
lat, lon = transformer.transform(x, y)
nueva_fila = pd.DataFrame({'id':[datos[0][0]],
                            'Tipo de tramo':[datos[0][1]],
                            'Tipo de seccion':[datos[0][2]], 
                            'zarriba':[datos[0][5]],
                            'zabajo':[datos[0][6]],
                            'lat':[lat],
                            'lon':[lon],
                            'x':[datos[0][14]],
                            'y':[datos[0][15]]})

data_frame = pd.concat([data_frame, nueva_fila])



print(str(data_frame))
fig = px.line_mapbox(data_frame, lat = 'lat', lon = 'lon', hover_name = 'id', hover_data = ['Tipo de tramo', 'Tipo de seccion', 'x', 'y'],
                        color_discrete_sequence=['rgba(200, 30, 100, 1)'], zoom = 19, height = 1000, center = dict(lat = lat, lon = lon), mapbox_style = 'open-street-map')




fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.write_html("map.html")