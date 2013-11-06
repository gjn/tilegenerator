#!/bin/bash

## Some docs:
# http://collectd.org/wiki/index.php/Plugin:Exec
# http://collectd.org/wiki/index.php/Plain_text_protocol#PUTVAL
# http://collectd.org/documentation/manpages/collectd.conf.5.shtml#plugin_exec
# http://collectd.org/documentation/manpages/collectd-exec.5.shtml#exec_data_format
# http://collectd.org/documentation/manpages/types.db.5.shtml
# http://manpages.debian.net/cgi-bin/man.cgi?query=rrdcreate


HOSTNAME="${COLLECTD_HOSTNAME:-`hostname -f`}"
INTERVAL="${COLLECTD_INTERVAL:-10}"

STAT_FOLDER=$1

# values order:
 # default: success count, failure count
 # rate   : success rate

while sleep "$INTERVAL"; do
    ls -1 "$STAT_FOLDER"/*  | while read file
    do
        LAYERNAME=$(echo "${file##*/}" | sed 's/[\.-]/_/g')
        VALUE="`awk -F\: '{print $1}' \"${file}\"`:`awk -F\: '{print $2}' \"${file}\"`"
        echo "PUTVAL $HOSTNAME/tileforge-$LAYERNAME/tileforge_tiles interval=$INTERVAL N:$VALUE"
        VALUE="`awk -F\: '{print $3}' \"$file\"`"
        echo "PUTVAL $HOSTNAME/tileforge-$LAYERNAME/tileforge_threads interval=$INTERVAL N:$VALUE"
        # Clear all values (U = undefined)
        echo "U:U:U" > $file
    done
done
