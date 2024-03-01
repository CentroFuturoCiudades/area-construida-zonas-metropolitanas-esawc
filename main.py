import ee
import subprocess
import numpy as np
import geopandas as gpd
import esawc_built as esa

def load_file(path_file):
    data = gpd.read_file(path_file)
    data = data.to_crs("EPSG:4326")
    return data


if __name__ == "__main__":
    # EE Authentication
    print("EE Authentication...")
    subprocess.run("earthengine authenticate --auth_mode=notebook", shell=True)
    ee.Initialize()
    print("Done")

    # Load Files
    print("Loading data file...")
    path_file = './input/metropoli.shp'
    data = load_file(path_file)
    size = len(data)
    print("Done")

    # Iterate over all places
    print("Calculation will start soon...")
    builtup_list = []
    for count, geometry in enumerate(data.geometry):
        # Print count
        if count%25 == 0:
            print('Step:', count, '/', size)
    
        
        # Complete computations!
        try:
            builtup_item = esa.get_builtup(geometry)
            builtup_list.append(builtup_item)
        except ValueError:
            builtup_list.append(np.nan)

    # New Columns
    print("Adding new column...")
    data["esa_builtup"] = builtup_list
    print("Done")
    
    # Save Geojson
    print("Saving new file...")
    data.to_file("./output/output.geojson", driver="GeoJSON")
    print("Done")