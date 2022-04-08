from osgeo import gdal, ogr, osr
from math import log
from numpy import *
import matplotlib.pyplot as plt
from pyproj import Proj
from Consts import Const
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from MyLib import HotPointsNew, Clouds, CreateRasterizeImage, CreateRasterize

hdf_ds = gdal.Open(Const.BANDS, gdal.GA_ReadOnly)
band_array = gdal.Open(hdf_ds.GetSubDatasets()[2][0], gdal.GA_ReadOnly)
band_array = band_array.ReadAsArray()

# clouds
refArray = gdal.Open(gdal.Open(Const.BANDS, gdal.GA_ReadOnly).GetSubDatasets()[4][0], gdal.GA_ReadOnly).ReadAsArray()
Earray = gdal.Open(gdal.Open(Const.BANDS, gdal.GA_ReadOnly).GetSubDatasets()[2][0], gdal.GA_ReadOnly).ReadAsArray()[11]
metadata = gdal.Open(hdf_ds.GetSubDatasets()[4][0]).GetMetadata()
reflectance_scales = list(map(float, metadata['reflectance_scales'].split(', ')))
reflectance_offsets = list(map(float, metadata['reflectance_offsets'].split(', ')))

metadata = gdal.Open(hdf_ds.GetSubDatasets()[2][0]).GetMetadata()
radiance_scales = list(map(float, metadata['radiance_scales'].split(', ')))
radiance_offsets = list(map(float, metadata['radiance_offsets'].split(', ')))
latitude = gdal.Open(f"HDF4_EOS:EOS_SWATH:{Const.GEOPOSITION}:MODIS_Swath_Type_GEO:Latitude",
                     gdal.GA_ReadOnly).ReadAsArray()
longitude = gdal.Open(f"HDF4_EOS:EOS_SWATH:{Const.GEOPOSITION}:MODIS_Swath_Type_GEO:Longitude",
                      gdal.GA_ReadOnly).ReadAsArray()
zenith = gdal.Open(f"HDF4_EOS:EOS_SWATH:{Const.GEOPOSITION}:MODIS_Swath_Type_GEO:SolarZenith",
                   gdal.GA_ReadOnly).ReadAsArray()
SeaMask = gdal.Open(f"HDF4_EOS:EOS_SWATH:{Const.GEOPOSITION}:MODIS_Swath_Type_GEO:Land/SeaMask",
                    gdal.GA_ReadOnly).ReadAsArray()

c2 = 1.4387752 * 10 ** 4
c1b = 1.19104282 * 10 ** 8
lam = {0: 3.750, 1: 3.959, 2: 3.959, 3: 4.050, 4: 4.465, 5: 4.515, 6: 6.715, 7: 7.325, 8: 8.550, 9: 9.730, 10: 11.030,
       11: 12.020, 12: 13.335, 13: 13.635, 14: 13.935, 15: 14.235}

# for i in range(14):
i = 3
'''# CreateRasterize(f'5x5 bufers\\{i + 1}.shp', f'{i + 1}.tif', 'cuut.tif')
CreateRasterizeImage('cuut.tif', f'{i + 1}.tif', i + 1)'''

ds = gdal.Open('cuut.tif', gdal.GA_ReadOnly)
channel1 = ds.GetRasterBand(1).ReadAsArray()
channel2 = ds.GetRasterBand(2).ReadAsArray()
channel3 = ds.GetRasterBand(3).ReadAsArray()
im = plt.imshow(channel3, cmap='rainbow')
plt.colorbar(im)
plt.show()















# ========================СОЗДАНИЕ РАСТРА===============================================================================
'''ny = len(layer)
nx = len(layer[0])

long, lat = p(longitude[0][0], latitude[0][0])
print(lat, long)
geotransform = (long - 14000, 1000, 0, lat, 0, -1000)

dst_ds = gdal.GetDriverByName('GTiff').Create('1.tif', nx, ny, 1, gdal.GDT_Byte)
dst_ds.SetGeoTransform(geotransform)
srs = osr.SpatialReference()
srs.ImportFromEPSG(32634)
wkt = PROJCS["WGS 84 / UTM zone 34N",
    GEOGCS["WGS 84",
        DATUM["WGS_1984",
            SPHEROID["WGS 84",6378137,298.257223563,
                AUTHORITY["EPSG","7030"]],
            AUTHORITY["EPSG","6326"]],
        PRIMEM["Greenwich",0,
            AUTHORITY["EPSG","8901"]],
        UNIT["degree",0.0174532925199433,
            AUTHORITY["EPSG","9122"]],
        AUTHORITY["EPSG","4326"]],
    PROJECTION["Transverse_Mercator"],
    PARAMETER["latitude_of_origin",0],
    PARAMETER["central_meridian",21],
    PARAMETER["scale_factor",0.9996],
    PARAMETER["false_easting",500000],
    PARAMETER["false_northing",0],
    UNIT["metre",1,
        AUTHORITY["EPSG","9001"]],
    AXIS["Easting",EAST],
    AXIS["Northing",NORTH],
    AUTHORITY["EPSG","32634"]]
dst_ds.SetProjection(wkt)
dst_ds.GetRasterBand(1).WriteArray(layer)'''
