import ee 
import geemap
from ipywidgets import Layout
from shapely.geometry import Polygon
     
def get_builtup_raster(polygon):
    #Get bbox of the Polygon
    bbox = get_bbox(polygon)

    # Get Earth Engine BBox
    bbox_ee = polygon_to_ee(bbox)
    
    # Get Raster
    dataset = ee.ImageCollection('ESA/WorldCover/v100')
    image = dataset.filterBounds(bbox_ee).first()
    image = image.clip(bbox_ee)
    mask = image.select('Map').eq(50)
    image = image.updateMask(mask)
    image = image.where(50,1)
    return image

def plot_builtup(polygon):
    # Get raster
    image = get_builtup_raster(polygon)

    # Get polygon's center
    lon, lat = polygon.centroid.x, polygon.centroid.y

    # Create a Map
    Map = geemap.Map(layout=Layout(width='80%', height='500px'))

    # Center
    Map.setCenter(lon, lat, 10)

    # VisParams
    vizParams = {
    'band': 'Map',
    'min': 0,
    'max': 1,
    'palette': ['FFFFFF', '000000']
    }

    # Add Layer
    Map.addLayer(image, vizParams, name = 'ESA WC')
    Map.addLayer(geometry_to_ee(polygon))

    ##Display the map
    return Map

def get_builtup(polygon, unweighted = False):
    '''
    Function to obtain Builtup Area (m2) from ESA WorldCover
    Input:
        - polygon: polygon of the roi (shapely object).
    Output:
        - bu_area: built-up area in m2.
    '''

    # Transform polygon to ee object
    polygon_ee = geometry_to_ee(polygon)

    # Get rasters
    image = get_builtup_raster(polygon)

    if unweighted:
        stats = image.reduceRegion(
        reducer = ee.Reducer.sum().unweighted(),
        geometry = polygon_ee,
        scale = 10,
        maxPixels = 1e12)
    else:
        stats = image.reduceRegion(
        reducer = ee.Reducer.sum(),
        geometry = polygon_ee,
        scale = 10,
        maxPixels = 1e12)

    
    bu_area = stats.getInfo()['Map']*100
    return bu_area

def get_bbox(polygon):
    '''
    Function to obtain get the bounding box of a given polygon
    Input:
        - polygon: polygon of the roi (shapely object).
    Output:
        - bu_area: bounding box of the polygon (shapely object).
    '''
    # Get Bounds
    bounds = polygon.bounds
    
    # Get BBox
    delta_lat = bounds[3] - bounds[1]
    delta_lon = bounds[2] - bounds[0]

    mid_lat = (bounds[3] + bounds[1])/2
    mid_lon = (bounds[2] + bounds[0])/2

    lat_max = mid_lat + delta_lat/2
    lat_min = mid_lat - delta_lat/2
    lon_max = mid_lon + delta_lon/2
    lon_min = mid_lon - delta_lon/2

    bbox = Polygon([(lon_min, lat_min), (lon_max, lat_min),
                    (lon_max, lat_max), (lon_min, lat_max)])
    return bbox

def geometry_to_ee(geometry):
    '''
    Function to convert a geometry (Polygon or Multipolygon) into an ee's object
    Input:
        - polygon or multipolygon: polygon or multipolygon of the roi (shapely object).
    Output:
        - ee's geometry: ee's geometry depending on input.
    '''
    geometry_type = geometry.geom_type
    if  geometry_type == 'Polygon':
        return polygon_to_ee(geometry)
    elif geometry_type == 'MultiPolygon':
        return ee.Geometry.MultiPolygon([polygon_to_ee(geom) for geom in list(geometry.geoms)])


    
def polygon_to_ee(polygon):
    '''
    Function to obtain convert the polygon (shapely object) into a ee's polygon
    Input:
        - polygon: polygon of the roi (shapely object).
    Output:
        - polygon_to_ee: ee's polygon of the roi (shapely object).
    '''

    polygon_to_ee = ee.Geometry.Polygon(
        [t for t in zip(*polygon.exterior.coords.xy)])

    return polygon_to_ee