=========================
 Running the tilemanager
=========================

.. note:: The ``tilemanager`` command described here tries to follow
  as much as possible the original ``tilecache_seed.py``.

Normal Mode
===========

The general command syntax is::

    tilemanager [options] <layername> [start_zoom stop_zoom]

The only mandatory options is the layer name (``<layername>``). The
two last arguments are the start and the end zoom levels separated by
a space. If these zooms are omitted, all the levels are generated.

Optional options:
 * ``-c config``: path to the tilecache configuration file. Default is
   ``tilecache.cfg``.
 * ``-b "minx, miny, maxx, maxy"``: the bounding box to
   generated. Default is the layer's bbox value found in the
   configuration file.
 * ``-t num``: the number of concurrent threads to run. Default is 5.

Examples
--------

Generate all the tiles of a layer::

    tilemanager -c /path/to/tilecache.cfg foobar

Generate only a subset of a layer, in this case only the two first
levels. The ``-c`` option is omitted: a ``tilecache.cfg`` file must be
present in the current directory::

    tilemanager foobar 0 2

Generate only a subset of a layer: the four first levels and a
specific bounding box, using ten threads::

    tilemanager -c /path/to/tilecache.cfg -t 10 -b "0,0,500,500" foobar 0 2

.. _retry-mode:

Retry Mode
==========
This mode is used to retry to generate a list of tiles::

    tilemanager [options] -r /path/to/tiles.retry

In this mode, the ``-b`` option, the layername and the zoom levels are
ignored; only the number of threads (``-t``) and/or the path to the
config  file (``-c``) can be specified.
