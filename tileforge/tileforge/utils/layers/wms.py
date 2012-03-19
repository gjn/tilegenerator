import urllib2
import httplib
from TileCache.Layers.WMS import WMS as TileCacheWMS
import TileCache.Client as WMSClient
import tileforge
import datetime

try:
    HIDE_ALL
except NameError:
    HIDE_ALL = False

class WMSClientHeader(WMSClient.WMS):
    def fetch (self):
        urlrequest = urllib2.Request(self.url())
        urlrequest.add_header("Referer", "http://tileforge.geo.admin.ch")
        urlrequest.add_header("User-Agent", "TileForge %s" % tileforge.__version__)
        response = None
        while response is None:
            try:
                response = self.client.open(urlrequest)
                data = response.read()
                # check to make sure that we have an image...
                msg = response.info()
                if msg.has_key("Content-Type"):
                    ctype = msg['Content-Type']
                    if ctype[:5].lower() != 'image':
                        if HIDE_ALL:
                            raise Exception("\n[%s] Did not get image data back. (Adjust HIDE_ALL for more detail.)" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                        else:
                            raise Exception("\n[%s] Did not get image data back. \nURL: %s\nContent-Type Header: %s\nResponse: \n%s" % ( datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") ,self.url(), ctype, data))
            except httplib.BadStatusLine:
                response = None # try again
        return data, response


class WMS(TileCacheWMS):
    def __init__ (self, *args, **kwargs):
        TileCacheWMS.__init__(self, *args, **kwargs)
        self.yorigin = kwargs.get('yorigin', 'bottom')

        self.wms_client = WMSClientHeader(self.url, {
          "srs": self.srs,
          "format": self.mime_type,
          "layers": self.layers,
        }, self.user, self.password)
        self.yshift_cache = {}

    def yshift(self, zoom):
        if zoom not in self.yshift_cache:
            if self.yorigin == 'top':
                resolution = self.resolutions[zoom]
                # height in pixel of the bbox
                p_height = (self.bbox[3] - self.bbox[1]) / resolution
                # height in pixel between the top of the bbox and the tile
                rem = (p_height % self.size[1])
                if rem > 0.0:
                    self.yshift_cache[zoom] = (self.size[1] - rem) * resolution
                else:
                    self.yshift_cache[zoom] = 0.0
            else:
                self.yshift_cache[zoom] = 0.0

        return self.yshift_cache[zoom]

    def renderTile(self, tile):
        minx, miny, maxx, maxy = tile.bounds()
        miny -= self.yshift(tile.z)
        maxy -= self.yshift(tile.z)

        self.wms_client.params['bbox'] = ",".join(map(str, [minx, miny, maxx, maxy]))

        w, h = tile.size()
        self.wms_client.params['width'] = w
        self.wms_client.params['height'] = h

        tile.data, response = self.wms_client.fetch()
        return tile.data
