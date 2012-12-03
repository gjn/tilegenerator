#! /bin/bash

# Start testperimeter generation for layer ch.swisstopo.zeitreihen ...
buildout/bin/tilemanager -t 64 -c etc/ch.swisstopo.zeitreihen/tilecache.swisstopo.zeitreihen.zoomlevel15.1952-1953.1952.cfg ch.swisstopo.zeitreihen 15 20 -b 655000,194000,672500,206000
buildout/bin/tilemanager -t 64 -c etc/ch.swisstopo.zeitreihen/tilecache.swisstopo.zeitreihen.zoomlevel15.1952-1953.1953.cfg ch.swisstopo.zeitreihen 15 20 -b 655000,194000,672500,206000

# Start tile generation for layer ch.swisstopo.zeitreihen ...
buildout/bin/tilemanager -t 64 -c etc/ch.swisstopo.zeitreihen/tilecache.swisstopo.zeitreihen.zoomlevel15.1952-1953.1952.cfg ch.swisstopo.zeitreihen 15 20
buildout/bin/tilemanager -t 64 -c etc/ch.swisstopo.zeitreihen/tilecache.swisstopo.zeitreihen.zoomlevel15.1952-1953.1953.cfg ch.swisstopo.zeitreihen 15 20



