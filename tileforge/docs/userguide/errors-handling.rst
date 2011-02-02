.. _errors-handling:

=================
 Errors Handling
=================

Behavior
========

At the end the generation process and if something went wrong a mail
is sent with detailed debug message (see :ref:`email-config`) along
with a *retry file*.

This binary file contains all the tiles that were not processed
correctly and can be passed to the ``tilemanager`` command to retry to
generated them: the syntax is described in the :ref:`retry-mode`
chapter.

Configuration
=============

In ``tilecache.cfg`` add the following options into the ``[metadata]``
section (create it if it doesn't exist)::

    [metadata]
    ...
    errors_dir = /path/to/tileforge/errors
    errors_generatemin = 10
    errors_succesratio = 1000

Where:
 * ``errors_dir``: The directory where the errors file must be
   written, the directory is created if it doesn’t exists. Default is
   ``/tmp/tileforge/errors``.
 * ``errors_generatemin``: fixme
 * ``errors_succesratio``: fixme


