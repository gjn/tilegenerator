#! /bin/bash

# Start testperimeter generation for layer ch.swisstopo.zeitreihen ...
buildout/bin/tilemanager -t 64 -c etc/ch.swisstopo.zeitreihen/tilecache.swisstopo.zeitreihen.zoomlevel15.1938-1951.1938.cfg ch.swisstopo.zeitreihen 15 16 -b 660000,194000,672500,206000
buildout/bin/tilemanager -t 64 -c etc/ch.swisstopo.zeitreihen/tilecache.swisstopo.zeitreihen.zoomlevel15.1952-1953.1952.cfg ch.swisstopo.zeitreihen 15 16 -b 660000,194000,672500,206000
buildout/bin/tilemanager -t 64 -c etc/ch.swisstopo.zeitreihen/tilecache.swisstopo.zeitreihen.zoomlevel15.1954-1964.1954.cfg ch.swisstopo.zeitreihen 15 16 -b 660000,194000,672500,206000
buildout/bin/tilemanager -t 64 -c etc/ch.swisstopo.zeitreihen/tilecache.swisstopo.zeitreihen.zoomlevel15.1965-2010.1965.cfg ch.swisstopo.zeitreihen 15 16 -b 660000,194000,672500,206000
buildout/bin/tilemanager -t 64 -c etc/ch.swisstopo.zeitreihen/tilecache.swisstopo.zeitreihen.zoomlevel20.1938-1953.1938.cfg ch.swisstopo.zeitreihen 20 21 -b 660000,194000,672500,206000
buildout/bin/tilemanager -t 64 -c etc/ch.swisstopo.zeitreihen/tilecache.swisstopo.zeitreihen.zoomlevel20.1954-1964.1954.cfg ch.swisstopo.zeitreihen 20 21 -b 660000,194000,672500,206000
buildout/bin/tilemanager -t 64 -c etc/ch.swisstopo.zeitreihen/tilecache.swisstopo.zeitreihen.zoomlevel20.1965-2010.1965.cfg ch.swisstopo.zeitreihen 20 21 -b 660000,194000,672500,206000
buildout/bin/tilemanager -t 64 -c etc/ch.swisstopo.zeitreihen/tilecache.swisstopo.zeitreihen.zoomlevel21.1938-1962.1938.cfg ch.swisstopo.zeitreihen 21 22 -b 660000,194000,672500,206000
buildout/bin/tilemanager -t 64 -c etc/ch.swisstopo.zeitreihen/tilecache.swisstopo.zeitreihen.zoomlevel21.1963-2010.1963.cfg ch.swisstopo.zeitreihen 21 22 -b 660000,194000,672500,206000
buildout/bin/tilemanager -t 64 -c etc/ch.swisstopo.zeitreihen/tilecache.swisstopo.zeitreihen.zoomlevel22.1938-1951.1938.cfg ch.swisstopo.zeitreihen 22 23 -b 660000,194000,672500,206000
buildout/bin/tilemanager -t 64 -c etc/ch.swisstopo.zeitreihen/tilecache.swisstopo.zeitreihen.zoomlevel22.1952-1978.1952.cfg ch.swisstopo.zeitreihen 22 23 -b 660000,194000,672500,206000
buildout/bin/tilemanager -t 64 -c etc/ch.swisstopo.zeitreihen/tilecache.swisstopo.zeitreihen.zoomlevel22.1979-2010.1979.cfg ch.swisstopo.zeitreihen 22 23 -b 660000,194000,672500,206000

