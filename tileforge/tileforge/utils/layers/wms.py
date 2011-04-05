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

    def renderTile(self, tile):
        size = tile.size()
        self.wms_client.params['width'] = size[0]
        self.wms_client.params['height'] = size[1]

        if self.yorigin == 'top':
            # tile origin if top left
            res  = tile.layer.resolutions[tile.z]
            minx = tile.layer.bbox[0] + (res * tile.x * tile.layer.size[0])
            miny = tile.layer.bbox[3] - (res * (tile.y + 1) * tile.layer.size[1])
            maxx = tile.layer.bbox[0] + (res * (tile.x + 1) * tile.layer.size[0])
            maxy = tile.layer.bbox[3] - (res * tile.y * tile.layer.size[1])

            self.wms_client.params['bbox'] = ",".join(map(str, [minx, miny, maxx, maxy]))
        else:
            # tile origin if bottom left
            self.wms_client.params['bbox'] = tile.bbox()

        tile.data, response = self.wms_client.fetch()
        return tile.data
