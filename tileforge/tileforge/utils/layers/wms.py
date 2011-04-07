from TileCache.Layers.WMS import WMS as TileCacheWMS
import TileCache.Client as WMSClient

class WMS(TileCacheWMS):
    def __init__ (self, *args, **kwargs):
        TileCacheWMS.__init__(self, *args, **kwargs)
        self.yorigin = kwargs.get('yorigin', 'bottom')

        self.wms_client = WMSClient.WMS(self.url, {
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
