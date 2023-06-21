import plotly.graph_objects as go
import numpy as np
from PIL import Image

def sphere(size, texture): 
    N_lat = int(texture.shape[0])
    N_lon = int(texture.shape[1])
    theta = np.linspace(0,2*np.pi,N_lat)
    phi = np.linspace(0,np.pi,N_lon)
    
    # Set up coordinates for points on the sphere
    x0 = size * np.outer(np.cos(theta),np.sin(phi))
    y0 = size * np.outer(np.sin(theta),np.sin(phi))
    z0 = size * np.outer(np.ones(N_lat),np.cos(phi))
    
    # Set up trace
    return x0,y0,z0

def plane(puntos_array):
    """" Devuelve un plano que pasa por tres puntos 
            PARAMETROS: `puntos_array` array de tres puntos por los que debe pasar el plano
    """
    v1Plano = np.array(puntos_array[1]) - np.array(puntos_array[0])
    v2Plano = np.array(puntos_array[2]) - np.array(puntos_array[0])
    normalPlano = np.cross(v1Plano, v2Plano)
    a, b, c = normalPlano
    d = np.dot(normalPlano, puntos_array[0])
    #print(f"{a}x +  {b}y +  {c}z  + {d} = 0")

    # Genera una malla de puntos en el plano

    X, Y = np.meshgrid(np.linspace(0, 533, 533), np.linspace(0, 800, 800))
    Z = (d - a*X - b*Y) / c
    return X, Y, Z


planet_name = 'acera'
Texture = np.asarray(Image.open('earth.jpg'.format(planet_name))).T
points = [[1, 0, 0], [0, 1, 0], [0,0,0]]
#rgb(30, 59, 117)
colorscale =[[0.0, 'rgb(80,80,180)'],
             
            [0.1, 'rgb(46, 680, 21)'],
            [0.2, 'rgb(74, 96, 280)'],
            [0.3, 'rgb(115,141,900)'],
            [0.4, 'rgb(122, 126, 750)'],

            [0.6, 'rgb(122, 1260, 75)'],
            [0.7, 'rgb(141,1015,96)'],
            [0.8, 'rgb(223, 197, 170)'],
            [0.9, 'rgb(237,214,183)'],

            [1.0, 'rgb(255, 255, 255)']]

# /* CSS HEX */
# --silver: #B9B6B4ff;
# --silver-2: #ADAAA8ff;
# --silver-3: #C5C3C3ff;
# --battleship-gray: #938F8Dff;
# --taupe: #403934ff;
# --silver-4: #CCCAC9ff;
# --taupe-gray: #A19F9Eff;
# --walnut-brown: #605953ff;
# --silver-5: #BEBCBBff;
# --gray: #817C78ff;
radius = 3
x,y,z = sphere(radius,Texture)
surf = go.Surface(x=x, y=y, z=z,
                  surfacecolor=Texture,
                  colorscale=colorscale)    

X, Y, Z = plane(points)
surf2 = go.Surface(x=X, y=Y, z=Z,
                  surfacecolor=Texture,
                  colorscale=colorscale)    

layout = go.Layout(scene=dict(aspectratio=dict(x=.5, y=.5, z=.5)))

fig = go.Figure(data=[surf2], layout=layout)

fig.write_html("texturePlanet.html")