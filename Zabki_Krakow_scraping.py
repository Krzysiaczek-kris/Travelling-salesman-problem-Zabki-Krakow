import requests
import pandas as pd
import geojson

url = "https://www.zabka.pl/app/uploads/locator-store-data.json"

headers = {
    "sec-ch-ua": "\"Microsoft Edge\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\""
}

referrer = "https://www.zabka.pl/znajdz-sklep/"

response = requests.get(url, headers=headers, allow_redirects=True)

if response.status_code == 200:
    print("Request successful!")
else:
    print(f"Request failed with status code: {response.status_code}")

json_data = response.json()
krakow_data = [store for store in json_data if store["town"] == "Kraków"]
df = pd.DataFrame(krakow_data)
df = df.drop_duplicates(subset=['lat', 'lon'], keep='first')
df = df[["street", "lat", "lon", "storeUrl"]]

features = []
for _, row in df.iterrows():
    point = geojson.Point((row["lon"], row["lat"]))
    properties = {
        "street": row["street"],
        "storeUrl": row["storeUrl"]
    }
    feature = geojson.Feature(geometry=point, properties=properties)
    features.append(feature)

feature_collection = geojson.FeatureCollection(features)

with open("data/Zabki_Krakow.geojson", "w") as f:
    geojson.dump(feature_collection, f)

print("Data saved to file: data/Zabki_Krakow.geojson", len(features))
