import geopandas as gpd
from shapely.geometry import Point
from tqdm import tqdm
import pandas as pd
from scipy.spatial import cKDTree
import numpy as np
from geopy.distance import geodesic

gdf_streets = gpd.read_file('data/Streets_Krakow.shp')
gdf_zabki = gpd.read_file('data/Zabki_Krakow.geojson')

gdf_streets.to_crs(epsg=4326, inplace=True)
gdf_zabki.to_crs(epsg=4326, inplace=True)

gdf_streets_exploded = gdf_streets.explode(index_parts=False)

all_street_points = gdf_streets_exploded.geometry.apply(lambda geom: [Point(coord) for coord in geom.coords])

all_street_points = [point for sublist in all_street_points for point in sublist]

gdf_street_points = gpd.GeoDataFrame(geometry=all_street_points)

street_points_tree = cKDTree(np.array(list(zip(gdf_street_points.geometry.x, gdf_street_points.geometry.y))))

def find_nearest(row, street_points_tree, gdf_street_points):
    point = row.geometry
    dist, idx = street_points_tree.query([point.x, point.y], k=1)
    nearest_point = gdf_street_points.iloc[idx].geometry
    distance = geodesic((point.y, point.x), (nearest_point.y, nearest_point.x)).meters
    return pd.Series({'street': row['street'], 'distance': distance, 'geometry': nearest_point})

gdf_nearest_points = gdf_zabki.apply(find_nearest, axis=1, street_points_tree=street_points_tree, gdf_street_points=gdf_street_points)

gdf_nearest_points = gpd.GeoDataFrame(gdf_nearest_points)
gdf_nearest_points.to_file('data/Nearest_points.geojson', driver='GeoJSON')
