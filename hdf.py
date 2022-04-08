from osgeo import gdal, ogr
from numpy import *
from pyproj import Proj
import matplotlib.pyplot as plt


ds = gdal.Open('L1C_T54TXT_A034963_20220303T012659.tif', gdal.GA_ReadOnly)
print(ds.GetGeoTransform())
print(ds.GetProjection())
X, stepX, alpha, Y, betta, stepY = ds.GetGeoTransform()
print(ds.RasterXSize, ds.RasterYSize, ds.RasterCount)
Xsize, Ysize, Rasters = ds.RasterXSize, ds.RasterYSize, ds.RasterCount
raster1 = ds.GetRasterBand(1).ReadAsArray()
raster2 = ds.GetRasterBand(2).ReadAsArray()
raster3 = ds.GetRasterBand(2).ReadAsArray()

vector = ogr.Open('1.shp')
coordinates = eval(vector.GetLayerByIndex(0).GetFeature(0).ExportToJson())['geometry']['coordinates'][0]
p = Proj(proj='utm', zone=54, ellps='WGS84', preserve_units=False)
points = list()
for coord in coordinates:
    x, y = p(*coord)
    print(x, y)
    points.append((round((x - X) / abs(stepX)), round(((y - Y) / abs(stepY)) * -1)))

im = plt.imshow(raster1, cmap='inferno')
plt.colorbar(im)
for x, y in points:
    plt.scatter(x, y, color='r')
plt.show()

'''fig, axes = plt.subplots(1, 3)

axes[0].imshow(raster1, cmap='inferno')
axes[0].set_title('band 1')

axes[1].imshow(raster2, cmap='inferno')
axes[1].set_title('band 2')

axes[2].imshow(raster3, cmap='inferno')
axes[2].set_title('band 3')

plt.show()'''
