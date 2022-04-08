from numpy import *
from Consts import Const
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from pyproj import Proj
from Consts import Const
from osgeo import gdal, ogr, osr
import matplotlib.pyplot as plt


def rec(elems, lst, alpha, pixels, size):
    elems_copy = elems.copy()
    new_coords = list()
    for e in elems_copy:
        y, x = e
        pixels.append((y, x))
        lst[y][x] = -1
        if x + 1 < size[0] and x - 1 >= 0 and y + 1 < size[1] and y - 1 >= 0:
            # fronts ----------------------
            if lst[y][x - 1] >= alpha:
                new_coords.append((y, x - 1))
            if lst[y + 1][x] >= alpha:
                new_coords.append((y + 1, x))
            if lst[y][x + 1] >= alpha:
                new_coords.append((y, x + 1))
            if lst[y - 1][x] >= alpha:
                new_coords.append((y - 1, x))
            # angles -----------------------
            if lst[y - 1][x - 1] >= alpha:
                new_coords.append((y - 1, x - 1))
            if lst[y + 1][x - 1] >= alpha:
                new_coords.append((y + 1, x - 1))
            if lst[y + 1][x + 1] >= alpha:
                new_coords.append((y + 1, x + 1))
            if lst[y - 1][x + 1] >= alpha:
                new_coords.append((y - 1, x + 1))
    new_coords = list(set(new_coords))
    if bool(new_coords):
        rec(new_coords, lst, alpha, pixels, size)
    return pixels


def HotPoints(T4, T11, longitude, latitude, startX, startY, v):
    POINTS = list()
    # size = (len(img[0]), len(img))
    new_img = T4.copy()
    count = 0
    for row, line in enumerate(new_img):
        for col, elem in enumerate(line):
            count += 1
            if elem >= v:
                count += 1
                POINTS.append([Const.IMAGEID,
                               count,
                               startY + row + 1,
                               startX + col + 1,
                               longitude[row][col],
                               latitude[row][col],
                               round(T4[row][col], 2),
                               round(T11[row][col], 2)])
    return POINTS


def HotPointsViaDelta(T4, T11, longitude, latitude, startX, startY, v):
    count = 0
    POINTS = list()
    for row, line in enumerate(T4 - T11):
        for col, elem in enumerate(line):
            count += 1
            if elem >= v:
                POINTS.append([Const.IMAGEID,
                               count,
                               startY + row + 1,
                               startX + col + 1,
                               longitude[row][col],
                               latitude[row][col],
                               round(T4[row][col], 2),
                               round(T11[row][col], 2)])
    return POINTS


def HotPointsNew(T4, T11, T2, longitude, latitude, startX, startY, Zenith, ref_scales, ref_offsets):
    T4mean = nanmean(T4) + 10
    dT = T4 - T11
    dTmean = nanmean(dT) + 5
    print(T4mean, dTmean)
    POINTS = list()
    step = T4.size // 100
    for row, (lineT4, lineDt, T2l, zenithL) in enumerate(zip(T4, dT, T2, Zenith)):
        for col, (pixel1, pixel2, T2v, ZenithV) in enumerate(zip(lineT4, lineDt, T2l, zenithL)):
            p0_85 = (ref_scales * (T2v - ref_offsets)) / cos(radians(ZenithV * 0.01))
            if pixel1 > T4mean and pixel2 > dTmean and p0_85 < 0.35:
                POINTS.append([Const.IMAGEID,
                               startY + row + 1,
                               startX + col + 1,
                               longitude[row][col],
                               latitude[row][col],
                               round(T4[row][col], 2),
                               round(T11[row][col], 2)])
            if ((row + 1) * (col + 1)) % step == 0:
                print(f'{((row + 1) * (col + 1)) // step}%')
    print('===="HotPointsNew" end====')
    return POINTS


def Clouds(AgT1, AgT2, ET12, Zenith, ref_scales, ref_offsets, time='day'):
    lst = list()
    step = AgT1.size // 100
    for row, (lAgT1, lAgT2, lET12, ZenithL) in enumerate(zip(AgT1, AgT2, ET12, Zenith)):
        line = list()
        for col, (T1v, T2v, ET12v, ZenithV) in enumerate(zip(lAgT1, lAgT2, lET12, ZenithL)):
            if time == 'day':
                p0_65 = (ref_scales[0] * (T1v - ref_offsets[0])) / cos(radians(ZenithV * 0.01))
                p0_85 = (ref_scales[1] * (T2v - ref_offsets[1])) / cos(radians(ZenithV * 0.01))
                if ((p0_65 + p0_85 > 1.2) or (ET12v < 265) or (p0_65 + p0_85 > 0.7 and ET12v < 285)) and ZenithV < 8500:
                    line.append(0)
                else:
                    line.append(1)
            else:
                if ET12v < 265:
                    line.append(0)
                else:
                    line.append(1)
            if ((row + 1) * (col + 1)) % step == 0:
                print(f'{((row + 1) * (col + 1)) // step}%')
        lst.append(line)
    lst = array(lst)
    print('===="Clouds" end====')
    return lst


def TerritoryMask(T4, vector, startLong, startLat, startCol, finishCol, startRow, finishRow):
    poly = list()
    p = Proj(proj='utm', zone=Const.UTM_zone, ellps='WGS84', preserve_units=False)
    startLong, startLat = tuple(map(int, p(startLong, startLat)))
    coordinates = eval(vector.GetLayerByIndex(0).GetFeature(0).ExportToJson().replace('null', 'None'))['geometry'][
        'coordinates']
    for long, lat in coordinates[0]:
        long, lat = p(long, lat)
        poly.append((abs(long - startLong) / 1000, (abs(lat - startLat) / 1000)))
    polygon = Polygon(poly)
    in_poly = list()
    for long, lat in coordinates[1]:
        long, lat = p(long, lat)
        in_poly.append((abs(long - startLong) / 1000, (abs(lat - startLat) / 1000)))
    in_polygon = Polygon(in_poly)
    # ------------------------------------------------------------------------------------------------------------------
    step = ((finishCol - startCol) * (finishRow - startRow)) // 100
    count = 1
    for row, line in enumerate(T4[startRow:finishRow, startCol:finishCol]):
        for col, elem in enumerate(line):
            if not polygon.contains(Point((col + startCol, row + startRow))):
                T4[row + startRow][col + startCol] = 0
            elif in_polygon.contains(Point((col + startCol, row + startRow))):
                T4[row + startRow][col + startCol] = 0
            count += 1
            if count % step == 0:
                print(str(count // step) + '%')
    return T4


def PointsInPolygon(data, vector, in_vector, longitude, latitude):
    polygon = Polygon(vector)
    if in_vector is not None:
        in_polygon = Polygon(in_vector)
    res = list()
    for imageid, row, col, long, lat, t4, t11 in data:
        if in_vector is not None:
            if polygon.contains(Point((longitude[row - 1][col - 1], latitude[row - 1][col - 1]))) and \
                    not in_polygon.contains(Point((longitude[row - 1][col - 1], latitude[row - 1][col - 1]))):
                res.append([imageid, row, col, long, lat, t4, t11])
        else:
            if polygon.contains(Point((longitude[row - 1][col - 1], latitude[row - 1][col - 1]))):
                res.append([imageid, row, col, long, lat, t4, t11])
    return res


def CreateRasterize(InFile, OutFile, TempFile):
    data = gdal.Open(TempFile, gdal.GA_ReadOnly)
    x_res = data.RasterXSize
    y_res = data.RasterYSize
    vector = ogr.Open(InFile)
    layer = vector.GetLayer()
    targetDataSet = gdal.GetDriverByName('GTiff').Create(OutFile, x_res, y_res, 3, gdal.GDT_Byte)
    targetDataSet.SetGeoTransform(data.GetGeoTransform())
    targetDataSet.SetProjection(data.GetProjection())
    band = targetDataSet.GetRasterBand(1)
    NoData_value = 0
    band.SetNoDataValue(NoData_value)
    band.FlushCache()
    gdal.RasterizeLayer(targetDataSet, [1, 2, 3], layer)
    data = None


def CreateRasterizeImage(TifFile, VectorTif, name=1):
    ds = gdal.Open(TifFile, gdal.GA_ReadOnly)
    ds_vector = gdal.Open(VectorTif, gdal.GA_ReadOnly)
    channel1v = ds_vector.GetRasterBand(1).ReadAsArray()
    channel1v[channel1v != 0] = 1
    X, stepX, aX, Y, aY, stepY = ds.GetGeoTransform()
    channel1 = ds.GetRasterBand(1).ReadAsArray() * channel1v
    channel2 = ds.GetRasterBand(2).ReadAsArray() * channel1v
    channel3 = ds.GetRasterBand(3).ReadAsArray() * channel1v

    if 1 in channel1v:
        startX = min([list(row).index(1) for row in channel1v if 1 in row]) - 1
        finishX = - min([list(row[::-1]).index(1) for row in channel1v if 1 in row])
        startY = min([list(channel1v[:, col]).index(1) for col in range(ds.RasterXSize) if 1 in channel1v[:, col]]) - 1
        finishY = - min([list(channel1v[::-1, col]).index(1) for col in range(ds.RasterXSize) if 1 in channel1v[:, col]])
        Nx = ds.RasterXSize - startX + finishX
        Ny = ds.RasterYSize - startY + finishY
        dst_ds = gdal.GetDriverByName('GTiff').Create(f'results\\res{name}.tif', Nx, Ny, 3, gdal.GDT_Byte)
        dst_ds.SetGeoTransform((X + stepX * startX, stepX, aX, Y + stepY * startY, aY, stepY))
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(Const.EPSG)
        dst_ds.SetProjection(ds.GetProjection())
        dst_ds.GetRasterBand(3).WriteArray(channel1[startY:finishY, startX:finishX])
        dst_ds.GetRasterBand(2).WriteArray(channel2[startY:finishY, startX:finishX])
        dst_ds.GetRasterBand(1).WriteArray(channel3[startY:finishY, startX:finishX])
        '''im = plt.imshow(channel1[startY:finishY, startX:finishX], cmap='rainbow')
        plt.colorbar(im)
        plt.show()'''
        dst_ds.FlushCache()
    ds = None
