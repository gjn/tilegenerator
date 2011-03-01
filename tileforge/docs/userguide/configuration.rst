.. _configuration:

===============
 Configuration
===============

This document describes the configuration options available in
extension of the standard TileCache file. For further information
about the TileCache configuration file syntax, please refer to the
`official documentation <http://tilecache.org/>`_

Layers configuration
====================

Vector Layers
-------------
To mark a layer as a vector layer, ``metadata_connection`` and the
``metadata_data`` must be set in the ``tilecache.cfg`` file::

    [layername]
    ...
    metadata_connection = "dbname=test user=postgres password=secret"
    metadata_data = "the_geom from table_a", "geom from table_b"

The options are:

 * ``metadata_connection`` is the database connection string; it's the
   same as the ``CONNECTION`` value found in the mapfile.

 * ``metadata_data`` is the SQL statement to execute to retrieve the
   geometry data from the PostGIS database; it's the same as the
   ``DATA`` value found in the mapfile. Multiple statements can be
   used here, they must be separated with a comma. All the statements must be
   contained inside a ``"`` pair.

.. note:: The ``metadata_data`` must not include the ``using unique
   [unique_key]`` or ``using srid=[spatial_reference_id]`` optional
   parameters which are not supported by tileforge (mapserver specific).

If no ``metadata_connection`` and ``metadata_data`` is found in the
configuration, the layer is considered as a raster layer and all the
tiles are generated.

WMTS Compatible Layers
----------------------
In order to save the tiles with a WMTS scheme and to build a valid
``WMTSCapabilities.xml`` document, all the layers must specify a
dimension, a matrix set identifier and the projection's unit.
These information must be set at the layer
level in the ``tilecache.cfg`` file::

    [layername]
    ...
    metadata_dimension = 1101311
    metadata_matrix_set = world4326
    units = meters

The ``metadata_matrix_set`` option defines the layer's TileMatrixSet
identifier, the default value is the layer name.

In addition, the base url of the tile server must be provided into the ``[metadata]``
section (create it if it doesn't exist), for example::

    [metadata]
    ...
    wmts_gettile = http://www.example.com/wmts/

Saving WMTS Capabilities
^^^^^^^^^^^^^^^^^^^^^^^^
If a ``wmts_capabilites_path`` option is set into the ``[metadata]``
section, the WMTS capabilities file will be saved there (via the cache
system).

Note that this feature is only available with a
``tileforge.utils.cache.s3.AWSS3`` cache.

Post-processing an image
------------------------
An arbitrary command can be run against the tiles before they are
saved into the cache. The command must be set at the layer level in
the tilecache.cfg file using the ``metadata_image_postproc`` option.

For instance, this can be used to reduce the size of a png image::

    [layername]
    ...
    metadata_image_postproc = optipng -q %filename

``%filename`` is the location of the image file, the updated file must
be saved at the same place.

The exit code of the command must be ``0``, otherwise it will be
considered as a failure.

Cache configuration
===================

FIXME: s3 cache setup::

    [cache]
    module = tileforge.utils.cache.s3
    type = AWSS3
    bucket_name = bucketname
    access_key = key
    secret_access_key = secret
    validate = true

Where:
 * ``module``: fixme.
 * ``type``: fixme.
 * ``bucket_name``: The bucket name to use to upload the tile, the
   bucket must already exists.
 * ``access_key``: The AWS access key.
 * ``secret_access_key``: The AWS secret access key.
 * ``validate``: ``true`` to check if the tile is really present in
   the bucket after the upload. Default is ``false``

.. _email-config:

E-Mails Configuration
=====================

In ``tilecache.cfg`` add the following options into the ``[metadata]``
section (create it if it doesn't exist)::

    [metadata]
    ...
    mail_to = admin@example.com, admin2@example.com

The options are:
 * ``mail_to``: List of addresses (comma-separated) that should
   receive error e-mails. If the option is empty, not e-mails are
   sent.
 * ``mail_from``: The e-mail address the manager sends e-mails
   from. Default is tileforge@example.com.
 * ``mail_subject_error``: The e-mail subject when something wrong
   happened while generating the tiles. Default is ``error while
   generating layer '%layer' on host '%host'``. ``%layer`` will be
   replaced with the layer name and ``%host`` with the hostname of
   the machine.
 * ``mail_subject_success``: The e-mail subject when all the tiles are
   generated without any errors. Default is ``all tiles generated for
   layer '%layer' on host '%host'``.
 * ``mail_server_host``: The mail server to use. Default is
   ``localhost``.
 * ``mail_server_port``: The port the mail server is listening
   on. Default is ``25``.
