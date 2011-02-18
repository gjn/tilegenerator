"""
Generate, postprocess and save tiles.
"""
import threading
import time
import logging

from TileCache.Layer import Tile
from tileforge.utils.file import run

class Generator(threading.Thread):
    def __init__(self, layer, cache, tiles, on_failure, on_success):
        threading.Thread.__init__(self)
        self.layer = layer
        self.cache = cache

        self.tiles = tiles
        self.on_failure = on_failure
        self.on_success = on_success
        self._abort = False

        self.postproc = self.layer.metadata.get("image_postproc")

        self.logger = logging.getLogger(__name__)

    def stop(self):
        """Stop this thread, if a tile is currently being processed
        it's finished first."""
        self._abort = True

    def run(self):
        try:
            self._run()
        except Exception, e:
            self.on_failure(None, fatal=True, message=str(e))

    def _run(self):
        for coords in self.tiles:
            if self._abort:
                return

            tile = Tile(self.layer, *coords)
            start = time.time()

            image = self.render(tile)
            if image is None:
                continue

            image = self.image_postproc(tile, image)
            if image is None:
                continue

            if self.save(tile, image):
                self.on_success(tile, duration=time.time() - start)

    def render(self, tile):
        """Render a tile using the TileCache layer instance.
        Returns the image data or None on error.
        """
        try:
            image = self.layer.render(tile)
        except Exception, e:
            self.on_failure(tile, message=str(e))
            return None
        return image

    def image_postproc(self, tile, image):
        """Post-process and image.
           Returns the updated image data or None on error.
        """
        if self.postproc is not None:
            try:
                image = run(image, self.postproc)
            except Exception, e:
                self.on_failure(tile, message=str(e))
                return None
        return image

    def save(self, tile, image):
        """Save the image into the TileCache cache instance.
           Returns True on success, False otherwise.
        """
        try:
            self.cache.set(tile, image)
        except Exception, e:
            self.on_failure(tile, message=str(e))
            return False
        return True
