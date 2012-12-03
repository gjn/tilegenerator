#! /bin/bash

# Start testperimeter generation for layer ch.swisstopo.zeitreihen ...
buildout/bin/tilemanager -t 64 -c etc/ch.swisstopo.zeitreihen/tilecache.swisstopo.zeitreihen.zoomlevel15.1938-1951.1938.cfg ch.swisstopo.zeitreihen 0 15 -b 655000,194000,672500,206000
buildout/bin/tilemanager -t 64 -c etc/ch.swisstopo.zeitreihen/tilecache.swisstopo.zeitreihen.zoomlevel15.1938-1951.1939.cfg ch.swisstopo.zeitreihen 0 15 -b 655000,194000,672500,206000



