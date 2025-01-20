import networkx as nx
import numpy as np
from geopy.distance import geodesic
import geopandas as gpd
from tqdm import tqdm
from joblib import Parallel, delayed


gdf_ulice = gpd.read_file('data/Streets_Krakow.shp')
gdf_nearest_points = gpd.read_file('data/Nearest_points.geojson')
gdf_ulice.to_crs(epsg=4326, inplace=True)
gdf_nearest_points.to_crs(epsg=4326, inplace=True)

# ------------------------------------------------------------
def create_street_graph(gdf_ulice):
    G = nx.Graph()
    
    for idx, row in tqdm(gdf_ulice.iterrows(), total=gdf_ulice.shape[0], desc='Creating graph'):
        coords = list(row['geometry'].coords)
        for i in range(len(coords) - 1):
            distance = geodesic(coords[i], coords[i + 1]).meters
            G.add_edge(coords[i], coords[i + 1], weight=distance)
    
    return G

def calculate_distance_matrix(gdf_nearest_points, street_graph):
    distance_matrix = np.zeros((gdf_nearest_points.shape[0], gdf_nearest_points.shape[0]))
    path_matrix = np.zeros((gdf_nearest_points.shape[0], gdf_nearest_points.shape[0]), dtype='object')

    def compute_row(i):
        row_distances = np.zeros(gdf_nearest_points.shape[0])
        row_paths = np.zeros(gdf_nearest_points.shape[0], dtype='object')
        point_i = gdf_nearest_points['geometry'].iloc[i].coords[0]
        distances, paths = nx.multi_source_dijkstra(street_graph, {point_i}, weight='weight')
        for j in range(gdf_nearest_points.shape[0]):
            if i != j:
                point_j = gdf_nearest_points['geometry'].iloc[j].coords[0]
                if point_j in distances:
                    row_distances[j] = distances[point_j]
                    row_paths[j] = paths[point_j]
        return i, row_distances, row_paths

    results = Parallel(n_jobs=-1)(
        delayed(compute_row)(i) 
        for i in tqdm(
            range(gdf_nearest_points.shape[0]), 
            desc='Calculating distances',
            total=gdf_nearest_points.shape[0]
        )
    )
    
    for i, row_distances, row_paths in results:
        distance_matrix[i, :] = row_distances
        path_matrix[i, :] = row_paths
    
    return distance_matrix, path_matrix

# ------------------------------------------------------------
street_graph = create_street_graph(gdf_ulice)

distance_matrix, path_matrix = calculate_distance_matrix(gdf_nearest_points, street_graph)

np.save('data/distance_matrix.npy', distance_matrix)
np.save('data/path_matrix.npy', path_matrix)
