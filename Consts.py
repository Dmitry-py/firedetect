class Const:
    BANDS = "hdfs\\20220408_072001_TERRA_MOD021KM.hdf"
    GEOPOSITION = "hdfs\\20220408_072001_TERRA_MOD03.hdf"
    VECTOR = "regions\\rosto.shp"
    UTM_zone = 37
    REGIONS = 'regions\\rastovrayon.shp'
    IMAGEID = BANDS[:-(BANDS[::-1].index('_') + 1)]
    EPSG = 32637
    DELTA = None
