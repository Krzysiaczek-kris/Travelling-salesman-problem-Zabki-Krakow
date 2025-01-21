import requests
import geopandas as gpd
from shapely.geometry import LineString
import networkx as nx

url = "https://overpass-api.de/api/interpreter"

headers = {
    "accept": "*/*",
    "accept-language": "pl,en;q=0.9,en-GB;q=0.8,en-US;q=0.7",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "sec-ch-ua": "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Microsoft Edge\";v=\"132\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
}

body = {
    "data": """[out:json];
area[name=\"Kraków\"]->.a;
(
  way[\"highway\"](area.a);
);
out center;
>;
out skel qt;"""
}

response = requests.post(url, headers=headers, data=body)

if response.status_code == 200:
    try:
        data = response.json()
        data = data["elements"]

    except ValueError as e:
        print(f"Error parsing JSON: {e}")
else:
    print(f"HTTP request error: {response.status_code}, {response.text}")

print("Data retrieved successfully. Processing...")

nodes = {node['id']: (node['lon'], node['lat']) for node in data if node['type'] == 'node'}

streets = []

for element in data:
    if element['type'] == 'way' and 'nodes' in element:
        try:
            coordinates = [nodes[node_id] for node_id in element['nodes']]
            geometry = LineString(coordinates)
            
            street_info = {
                "id": element["id"],
                "name": element["tags"].get("name", "unknown"),
                "highway": element["tags"].get("highway", "unknown"),
                "geometry": geometry
            }
            streets.append(street_info)
        except KeyError as e:
            print(f"Node not found for way {element['id']}: {e}")

streets_gdf = gpd.GeoDataFrame(streets, crs="EPSG:4326")

# Not all streets are connected, so we need to filter out smaller components
print("Finding connected street network...")

G = nx.Graph()

for idx, row in streets_gdf.iterrows():
    coords = list(row.geometry.coords)
    start = coords[0]
    end = coords[-1]
    G.add_edge(start, end, id=row.id)

components = list(nx.connected_components(G))

largest_component = max(components, key=len)

connected_edges = set()
for node in largest_component:
    for neighbor in G[node]:
        if neighbor in largest_component:
            edge_data = G[node][neighbor]
            connected_edges.add(edge_data['id'])

streets_gdf = streets_gdf[streets_gdf['id'].isin(connected_edges)]

streets_gdf.to_file("data/Streets_Krakow.shp")

print("Processing completed. Output saved to 'data/Streets_Krakow.shp'")