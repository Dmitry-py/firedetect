from osgeo import gdal, ogr, osr
from numpy import *
import matplotlib.pyplot as plt
from pyproj import Proj
from MyLib import HotPoints, TerritoryMask, Clouds, HotPointsViaDelta, HotPointsNew, PointsInPolygon
from Consts import Const

# -------------------------------CONSTANTS------------------------------------------------------------------------------
bands_file = Const.BANDS
geoposition_file = Const.GEOPOSITION
startCol, finishCol = 0, -1
startRow, finishRow = 0, -1
# -------------------------------MAIN---FILE----------------------------------------------------------------------------
hdf_ds = gdal.Open(bands_file, gdal.GA_ReadOnly)
band_array = gdal.Open(hdf_ds.GetSubDatasets()[2][0], gdal.GA_ReadOnly).ReadAsArray()
refArray = gdal.Open(gdal.Open(Const.BANDS, gdal.GA_ReadOnly).GetSubDatasets()[4][0], gdal.GA_ReadOnly).ReadAsArray()
# -------------------------------REFLECTANCES---------------------------------------------------------------------------
metadata = gdal.Open(hdf_ds.GetSubDatasets()[4][0]).GetMetadata()
reflectance_scales = list(map(float, metadata['reflectance_scales'].split(', ')))
reflectance_offsets = list(map(float, metadata['reflectance_offsets'].split(', ')))
# -------------------------------RADIANCES------------------------------------------------------------------------------
metadata = gdal.Open(hdf_ds.GetSubDatasets()[2][0]).GetMetadata()
radiance_scales = list(map(float, metadata['radiance_scales'].split(', ')))
radiance_offsets = list(map(float, metadata['radiance_offsets'].split(', ')))
# -------------------------------LATITUDE----LONGITUDE----ZENITH--------------------------------------------------------
latitude = gdal.Open(f"HDF4_EOS:EOS_SWATH:{geoposition_file}:MODIS_Swath_Type_GEO:Latitude",
                     gdal.GA_ReadOnly).ReadAsArray()
longitude = gdal.Open(f"HDF4_EOS:EOS_SWATH:{geoposition_file}:MODIS_Swath_Type_GEO:Longitude",
                      gdal.GA_ReadOnly).ReadAsArray()
zenith = gdal.Open(f"HDF4_EOS:EOS_SWATH:{Const.GEOPOSITION}:MODIS_Swath_Type_GEO:SolarZenith",
                   gdal.GA_ReadOnly).ReadAsArray()
SeaMask = gdal.Open(f"HDF4_EOS:EOS_SWATH:{Const.GEOPOSITION}:MODIS_Swath_Type_GEO:Land/SeaMask",
                   gdal.GA_ReadOnly).ReadAsArray()
startLong, startLat = longitude[0][0], latitude[0][0]
# ------------------------------VECTOR----FILES-------------------------------------------------------------------------
vector = ogr.Open(Const.VECTOR)
coordinates = eval(vector.GetLayerByIndex(0).GetFeature(0).ExportToJson().replace('null', 'None'))['geometry']['coordinates']
# ======================================================================================================================
# -------------------------------temperature---layers-------------------------------------------------------------------
c2 = 1.4387752 * 10 ** 4
c1b = 1.19104282 * 10 ** 8
lam = {0: 3.750, 1: 3.959, 2: 3.959, 3: 4.050, 4: 4.465, 5: 4.515, 6: 6.715, 7: 7.325, 8: 8.550, 9: 9.730, 10: 11.030,
       11: 12.020, 12: 13.335, 13: 13.635, 14: 13.935, 15: 14.235}
Ll = (lambda v: (c2 / lam[I]) / log(1 + (c1b * lam[I] ** -5) / (radiance_scales[I] * (v - radiance_offsets[I]))))
I = 10
T11 = Ll(band_array[I])
I = 1
T4 = Ll(band_array[I])
I = 11
E12 = Ll(band_array[I])
# --------------------------------CLOUD---AND---SEA---MASKING-----------------------------------------------------------
CloudMask = Clouds(refArray[0], refArray[1], E12, zenith, reflectance_scales, reflectance_offsets)
SeaMask[SeaMask == 0] = 1
SeaMask[SeaMask != 1] = 0
NoGroundMask = CloudMask * SeaMask
# ------------------------------------HOT---POINTS----------------------------------------------------------------------
points = list()
p = Proj(proj='utm', zone=Const.UTM_zone, ellps='WGS84', preserve_units=True)

hot_points = HotPointsNew(T4, T11, refArray[1], longitude, latitude, startCol, startRow, zenith,
                   reflectance_scales[1], reflectance_offsets[1])

hot_points = PointsInPolygon(hot_points, coordinates[0], None, longitude, latitude)
print('Hot points:', len(hot_points))

im = plt.imshow(T4 * NoGroundMask, cmap='rainbow')
plt.colorbar(im)

if hot_points is not None or bool(hot_points):
    for j, (_, row, col, long, lat, t4, t11) in enumerate(hot_points):
        plt.scatter(col - 1, row - 1, c='r', alpha=0.5)
        points.append((row - 1, col - 1))
        hot_points[j].insert(1, j + 1)

    with open('points.txt', 'w', encoding='UTF-8') as txt:
        txt.write(str(hot_points))
        txt.write('\n')
        txt.write(str(points))
plt.show()
