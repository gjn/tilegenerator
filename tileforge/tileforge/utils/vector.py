import logging
import re
from struct import pack
from osgeo import ogr

from TileCache.Layer import MetaTile, Tile
from tileforge.utils.layer import grid

logger = logging.getLogger(__name__)

def polygon(bbox):
    minx, miny, maxx, maxy = bbox
    wkt = "POLYGON((%d %d,%d %d,%d %d,%d %d,%d %d))"%(minx, miny, 
                                                      minx, maxy, 
                                                      maxx, maxy, 
                                                      maxx, miny, 
                                                      minx, miny)
    return ogr.CreateGeometryFromWkt(wkt)

def vector(tcLayer, bounds, levels, connection, data):
    # http://www.gdal.org/ogr/classOGRDataSource.html#a6acc228db6513784a56ce12334a8c33
    pad = pack('x')
    tiles = {}
    ogrBounds = polygon(bounds)

    ds = ogr.Open("PG:%s"%connection.strip('"'))
    if ds is None:
        raise Exception("PGconnectdb failed: '%s'"%connection)
    assert ds is not None

    for sql in re.split('"\W*"', data):
        layer = ds.ExecuteSQL("SELECT " + sql.strip('" '), ogrBounds)
        if layer is not None:
            layer.ResetReading()

            for geometry in (f.GetGeometryRef() for f in layer):
                minx, maxx, miny, maxy = geometry.GetEnvelope()
                # dont generate all tile for the whole feature if it is larger than the requested bbox
                logger.debug('feature bbox: ' + str(minx) + ' ' + str(miny) + ' ' + str(maxx) + ' ' + str(maxy))
                nminx = max(min(minx,maxx),min(bounds[0],bounds[2]))
                nminy = max(min(miny,maxy),min(bounds[1],bounds[3]))
                nmaxx = min(max(minx,maxx),max(bounds[0],bounds[2]))
                nmaxy = min(max(miny,maxy),max(bounds[1],bounds[3]))
                logger.debug('final bbox: ' + str(nminx) + ' ' + str(nminy) + ' ' + str(nmaxx) + ' ' + str(nmaxy))
                
                for x, y, z in grid(tcLayer, (nminx, nminy, nmaxx, nmaxy), levels, use_buffer=True):
                    tile = pack('3i', x, y, z)
                    if tile not in tiles:
                        metatile = MetaTile(tcLayer, x, y, z)
                        tminx, tminy, tmaxx, tmaxy = metatile.bounds()
                        shift = tcLayer.yshift(z) if hasattr(tcLayer, 'yshift') else 0.0
                        tminy -= shift
                        tmaxy -= shift
                        if geometry.Intersect(polygon((tminx, tminy, tmaxx, tmaxy))):
                            tiles[tile] = pad
                            yield (x, y, z) 
            ds.ReleaseResultSet(layer)
    ds.Destroy()

