import pandas as pd
import pyproj
import plotly.express as px
import plotly.graph_objects as go



tramos = pd.read_csv('Datos.csv')


transformer = pyproj.Transformer.from_crs("EPSG:32721", "EPSG:4326")


coords_puntos =  tramos.iloc[int(77)][16]
array_puntos = str(coords_puntos).split(",")
print(str(len(array_puntos)))
for i in range(0, len(array_puntos)):
    array_aux = array_puntos[i].split(" ")
    x = float(array_aux[1].split("(")[1])
    y = float(array_aux[2])
    
    lat, lon = transformer.transform(x, y)

    data_frame =  pd.DataFrame({
                                'lat':[lat],
                                'lon':[lon]})

    map_tramo = go.Scattermapbox(
        mode = 'lines',
        marker = go.scattermapbox.Marker(
            size = 9,
            color = 'rgba(200, 30, 100, 1)',
            
        )
    )

    fig = go.Figure(data = [map_tramo])
    fig.update_layout(
        mapbox = dict(
            accesstoken='pk.eyJ1IjoibmFodWVsMDAwIiwiYSI6ImNsZW11MGQ2YjAweXUzcnIxaHp4MTF2NGgifQ.aLPRn5aR6GNJ3QDIKbhFeg',
            style = 'light', 
            center = go.layout.mapbox.Center(
                lat = lat/2,
                lon = lon/2
            ),
            zoom = 18
        ),

    )


fig.update_layout(margin={"r":0,"t":5,"l":5,"b":5})
fig.write_html("map.html")