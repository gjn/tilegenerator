============
 Monitoring
============

Configuration
====================

The stats destination and frequency can be configured in
``tilecache.cfg`` into the ``[metadata]`` section (create it if it
doesn't exist):: 

    [metadata]
    ...
    stats_dir = /path/to/tileforge/stats
    stats_interval = 5
    
The options are:
 * ``stats_dir``: The directory where the file must be written, the
   directory is created if it doesn't exists. Default is
   ``/var/sig/tileforge/stats``. This is as present in the collectd 
   configuration file /var/lib/puppet/modules/collectd/plugins/tileforge.conf.
 * ``stats_interval``: The write frequency in seconds. Default is
   ``2`` seconds.

