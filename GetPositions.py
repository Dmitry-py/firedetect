from osgeo import ogr
from Consts import Const
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from osgeo import gdal

latitude = gdal.Open(f"HDF4_EOS:EOS_SWATH:{Const.GEOPOSITION}:MODIS_Swath_Type_GEO:Latitude",
                     gdal.GA_ReadOnly).ReadAsArray()
longitude = gdal.Open(f"HDF4_EOS:EOS_SWATH:{Const.GEOPOSITION}:MODIS_Swath_Type_GEO:Longitude",
                      gdal.GA_ReadOnly).ReadAsArray()

vector = ogr.Open(Const.REGIONS)
count = vector.GetLayerByIndex(0).GetFeatureCount()

with open('points.txt', 'r') as txt:
    points = eval(txt.readlines()[0])
    print(len(points))

for i in range(count):
    obj = eval(vector.GetLayerByIndex(0).GetFeature(i).ExportToJson().replace('null', 'None'))
    if len(obj['geometry']['coordinates'][0]) >= 3:
        poly = Polygon(obj['geometry']['coordinates'][0])
        for j, elem in enumerate(points):
            row, col = elem[2], elem[3]
            if poly.contains(Point((longitude[row - 1][col - 1], latitude[row - 1][col - 1]))):
                points[j].insert(len(elem), obj['properties']['name'])
                break

with open('points.txt', 'w', encoding='UTF-8') as file:
    file.write(str(points))
