from osgeo import ogr, osr, gdal
from pyproj import Proj
from Consts import Const

lat = gdal.Open(f"HDF4_EOS:EOS_SWATH:{Const.GEOPOSITION}:MODIS_Swath_Type_GEO:Latitude",
                gdal.GA_ReadOnly).ReadAsArray()
long = gdal.Open(f"HDF4_EOS:EOS_SWATH:{Const.GEOPOSITION}:MODIS_Swath_Type_GEO:Longitude",
                 gdal.GA_ReadOnly).ReadAsArray()

multipolygon = ogr.Geometry(ogr.wkbMultiPolygon)
with open('points.txt', 'r', encoding='UTF-8') as txt:
    lines = txt.readlines()
    points = eval(lines[1])
    points_to_csv = eval(lines[0][:-1])
print(len(points_to_csv))
p = Proj(proj='utm', zone=Const.UTM_zone, ellps='WGS84', preserve_units=True)
'''for i, (long, lat) in enumerate(points):
    pol_to_csv = ogr.Geometry(ogr.wkbLinearRing)
    pol_to_csv.AddPoint(*p(long - 2500, lat - 2500, inverse=True))
    pol_to_csv.AddPoint(*p(long + 2500, lat - 2500, inverse=True))
    pol_to_csv.AddPoint(*p(long + 2500, lat + 2500, inverse=True))
    pol_to_csv.AddPoint(*p(long - 2500, lat + 2500, inverse=True))
    pol_to_csv.AddPoint(*p(long - 2500, lat - 2500, inverse=True))
    polygon_to_csv = ogr.Geometry(ogr.wkbPolygon)
    polygon_to_csv.AddGeometry(pol_to_csv)
    points_to_csv[i].append(polygon_to_csv.ExportToWkt())
    points_to_csv[i].append()
    pol = ogr.Geometry(ogr.wkbLinearRing)
    pol.AddPoint(long - 2500, lat - 2500)
    pol.AddPoint(long + 2500, lat - 2500)
    pol.AddPoint(long + 2500, lat + 2500)
    pol.AddPoint(long - 2500, lat + 2500)
    pol.AddPoint(long - 2500, lat - 2500)
    polygon = ogr.Geometry(ogr.wkbPolygon)
    polygon.AddGeometry(pol)
    multipolygon.AddGeometry(polygon)'''

for i, (row, col) in enumerate(points):
    row -= 1
    col -= 1
    pol_to_csv = ogr.Geometry(ogr.wkbLinearRing)
    pol_to_csv.AddPoint((float(long[row - 1][col - 1]) + float(long[row][col])) / 2,
                        (float(lat[row - 1][col - 1]) + float(lat[row][col])) / 2)
    pol_to_csv.AddPoint((float(long[row - 1][col + 1]) + float(long[row][col])) / 2,
                        (float(lat[row - 1][col + 1]) + float(lat[row][col])) / 2)
    pol_to_csv.AddPoint((float(long[row + 1][col + 1]) + float(long[row][col])) / 2,
                        (float(lat[row + 1][col + 1]) + float(lat[row][col])) / 2)
    pol_to_csv.AddPoint((float(long[row + 1][col - 1]) + float(long[row][col])) / 2,
                        (float(lat[row + 1][col - 1]) + float(lat[row][col])) / 2)
    pol_to_csv.AddPoint((float(long[row - 1][col - 1]) + float(long[row][col])) / 2,
                        (float(lat[row - 1][col - 1]) + float(lat[row][col])) / 2)
    polygon_to_csv = ogr.Geometry(ogr.wkbPolygon)
    polygon_to_csv.AddGeometry(pol_to_csv)
    points_to_csv[i].append(polygon_to_csv.ExportToWkt())
    # ---------------------------------------------------Polygon to shp-------------------------------------------------
    pol = ogr.Geometry(ogr.wkbLinearRing)
    pol.AddPoint(*p((long[row - 1, col - 1] + long[row][col]) / 2, (lat[row - 1, col - 1] + lat[row][col]) / 2))
    pol.AddPoint(*p((long[row - 1, col + 1] + long[row][col]) / 2, (lat[row - 1, col + 1] + lat[row][col]) / 2))
    pol.AddPoint(*p((long[row + 1, col + 1] + long[row][col]) / 2, (lat[row + 1, col + 1] + lat[row][col]) / 2))
    pol.AddPoint(*p((long[row + 1, col - 1] + long[row][col]) / 2, (lat[row + 1, col - 1] + lat[row][col]) / 2))
    pol.AddPoint(*p((long[row - 1, col - 1] + long[row][col]) / 2, (lat[row - 1, col - 1] + lat[row][col]) / 2))
    polygon = ogr.Geometry(ogr.wkbPolygon)
    polygon.AddGeometry(pol)
    multipolygon.AddGeometry(polygon)
    # ------------------------------------Polygons 5x5------------------------------------------------------------------
    pol5 = ogr.Geometry(ogr.wkbLinearRing)
    pol5.AddPoint(*p(long[row - 2, col - 2], lat[row - 2, col - 2]))
    pol5.AddPoint(*p(long[row - 2, col + 2], lat[row - 2, col + 2]))
    pol5.AddPoint(*p(long[row + 2, col + 2], lat[row + 2, col + 2]))
    pol5.AddPoint(*p(long[row + 2, col - 2], lat[row + 2, col - 2]))
    pol5.AddPoint(*p(long[row - 2, col - 2], lat[row - 2, col - 2]))
    polygon5 = ogr.Geometry(ogr.wkbPolygon)
    polygon5.AddGeometry(pol5)
    driver = ogr.GetDriverByName("ESRI Shapefile")
    ds = driver.CreateDataSource(f"5x5 bufers\\{i + 1}.shp")
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(Const.EPSG)
    layer = ds.CreateLayer("lines", srs, ogr.wkbPolygon)
    idField = ogr.FieldDefn("id", ogr.OFTInteger)
    layer.CreateField(idField)
    featureDefn = layer.GetLayerDefn()
    feature = ogr.Feature(featureDefn)
    feature.SetGeometry(polygon5)
    feature.SetField("id", 1)
    layer.CreateFeature(feature)


driver = ogr.GetDriverByName("ESRI Shapefile")
ds = driver.CreateDataSource("shp\\bufers.shp")
srs = osr.SpatialReference()
srs.ImportFromEPSG(Const.EPSG)
layer = ds.CreateLayer("lines", srs, ogr.wkbMultiPolygon)
idField = ogr.FieldDefn("id", ogr.OFTInteger)
layer.CreateField(idField)
featureDefn = layer.GetLayerDefn()
feature = ogr.Feature(featureDefn)
feature.SetGeometry(multipolygon)
feature.SetField("id", 1)
layer.CreateFeature(feature)

with open('points.txt', 'w', encoding='UTF-8') as file:
    file.write(str(points_to_csv))
