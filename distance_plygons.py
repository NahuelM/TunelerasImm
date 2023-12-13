from shapely.geometry import MultiPolygon, Point, Polygon
import re
import numpy as np
# Definir las coordenadas de un MultiPolygon

# Definir un Point
point = Point(574291.185, 6137887.813)

# Calcular la distancia entre los dos puntos

# Coordenadas en cadena del MultiPolygon
coord_string = "MULTIPOLYGON(((574311.2814135746 6137915.796495833,574320.0655197642 6137921.316935031,574326.2324154476 6137900.501804421,574318.4690509748 6137897.713503937,574311.2814135746 6137915.796495833)))"

# Extraer las coordenadas internas del MultiPolygon
match = re.match(r"MULTIPOLYGON\(\(\((.*)\)\)\)", coord_string)
if match:
    # coordinates = match.group(1)
    # # Convertir las coordenadas en una lista de listas
    # coords_list = [list(map(float, coord.split())) for coord in coordinates.split(',')]
    # # Crear un objeto Polygon
    # polygon = Polygon(coords_list)
    # d = polygon.distance(point)
    # print("Distancia:", d)
    coordinates = match.group(1)
    coords_list = [list(map(float, coord.split())) for coord in coordinates.split(',')]
    polygon = Polygon(coords_list)

    # Calcular la distancia mínima entre el punto y los vértices del polígono
    distances = [point.distance(Point(coord)) for coord in coords_list]
    min_distance_index = np.argmin(distances)
    closest_vertex_coords = coords_list[min_distance_index]

    d = distances[min_distance_index]
    print("Distancia:", d)
    print("Coordenadas del punto más cercano dentro del polígono:", closest_vertex_coords)
else:
    print("No se pudieron extraer las coordenadas del MultiPolygon")

if match:
    coordinates = match.group(1)
    # Convertir las coordenadas en una lista de listas
    coords_list = [list(map(float, coord.split())) for coord in coordinates.split(',')]
    # Crear un objeto Polygon
    polygon = Polygon(coords_list)
    d = polygon.distance(point)
    print("Distancia:", d)


