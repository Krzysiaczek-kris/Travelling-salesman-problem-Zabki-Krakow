# Travelling Salesman Problem Żabki Kraków

This project solves the Travelling Salesman Problem (TSP) by finding shortest possible path that visits all Żabka stores in Kraków, Poland, exactly once. Streets in Kraków sourced from OpenStreetMap (OSM), are used as possible travel paths between stores.

## File contents

- `Zabki_Krakow_scraping.py`: Script for scraping Żabka store locations from official website.
- `Streets_Krakow_scraping.py`: Script for scraping and processing steet data in Kraków from OSM API.
- `Zabki_EDA.ipynb`: Identifies and removes duplicate Żabka store entries.
- `Preprocessing.py`: Maps store locations to the nearest points on the street network for use in distance calculations.
- `Distance_matrix.py`: Calculates the distance and path matrices for all stores.
- `TSP_nx.ipynb`: Demonstrates an example TSP solution using the NetworkX library.
- `TSP.py`: Solves the TSP using a Genetic Algorithm to find optimal route.
- `Results.ipynb`: Showcases the result and generates an animation of the optimal route (`best_path_animation.gif`).
