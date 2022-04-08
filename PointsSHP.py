from osgeo import ogr, osr, gdal
from Consts import Const
from pyproj import Proj

lat = gdal.Open(f"HDF4_EOS:EOS_SWATH:{Const.GEOPOSITION}:MODIS_Swath_Type_GEO:Latitude",
                gdal.GA_ReadOnly).ReadAsArray()
long = gdal.Open(f"HDF4_EOS:EOS_SWATH:{Const.GEOPOSITION}:MODIS_Swath_Type_GEO:Longitude",
                 gdal.GA_ReadOnly).ReadAsArray()

p = Proj(proj='utm', zone=Const.UTM_zone, ellps='WGS84', preserve_units=True)
multipoint = ogr.Geometry(ogr.wkbMultiPoint)
with open('points.txt', 'r', encoding='UTF-8') as txt:
    lines = txt.readlines()
    points = eval(lines[1])

for j, (row, col) in enumerate(points):
    point = ogr.Geometry(ogr.wkbPoint)
    point.AddPoint(*p(long[row - 1][col - 1], lat[row - 1][col - 1]))
    multipoint.AddGeometry(point)

driver = ogr.GetDriverByName("ESRI Shapefile")
ds = driver.CreateDataSource("shp\\fires.shp")
srs = osr.SpatialReference()
srs.ImportFromEPSG(Const.EPSG)
layer = ds.CreateLayer("points", srs, ogr.wkbMultiPoint)
idField = ogr.FieldDefn("id", ogr.OFTInteger)
layer.CreateField(idField)
featureDefn = layer.GetLayerDefn()
feature = ogr.Feature(featureDefn)
feature.SetGeometry(multipoint)
feature.SetField("id", 1)
layer.CreateFeature(feature)

feature = None
ds = None
