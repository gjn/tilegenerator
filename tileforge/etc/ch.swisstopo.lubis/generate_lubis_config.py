#!/usr/bin/env python
# coding=utf-8
#******************************************************************************
# 
#  Name:        generate_lubis_config.py
#  Project:     BGDI LUBIS
#  Purpose:     Utility to create tilecache cfg files for requested years
#               for the layers:
#                   * ch.swisstopo.lubis-luftbilder_farbe
#                   * ch.swisstopo.lubis-luftbilder_infrarot
#                   * ch.swisstopo.lubis-luftbilder_schwarzweiss
#                   * ch.swisstopo.lubis-luftbilder-dritte_firmen
#                   * ch.swisstopo.lubis-luftbilder-dritte_kantone
#
#  Author:      Clausen Marcel
# 
#******************************************************************************
#  
#  Verwendung/Zweck:
#  + Benutzt config template tilecache.swisstopo.lubis.YYYY.cfg
#  + generiert aus dem template tilecache.cfg Dateien für die gewünschten Jahre
#  + generiert bash scripte zum generieren der tiles
#
#******************************************************************************

import os,glob,sys,optparse,shutil,fileinput,psycopg2,sqlite3
from optparse import OptionParser

if __name__ == '__main__':
    ################################
    # Command Line Argument Parsing
    ################################

    epilog = """Examples:
    Beispiel 1: generiere tilecache config aus der db quelle lubis.public.view_luftbilder_* :
    python generate_lubis_config.py -o config -h localhost
    
    Beispiel 2: Generiere ein bash Script zur Tilegenerierung aus der db quelle lubis.public.view_luftbilder_*
    python generate_lubis_config.py -o bash -h localhost
    \n"""

    OptionParser.format_epilog = lambda self, formatter: self.epilog
    parser = OptionParser(epilog=epilog)
    parser.add_option("-o","--output", dest="output", 
                  help="Year Start")

    parser.add_option("--host", dest="host", 
                  help="db host")

    (options, args) = parser.parse_args()
    
    # -o is mandatory
    if options.output not in ['config','bash'] :
        parser.print_help()
        sys.exit( 1 )

    # -h is mandatory
    if options.host is None:
        parser.print_help()
        sys.exit( 1 )

    ################################
    # Variablen
    ################################
    template = 'tilecache.swisstopo.lubis.YYYY.cfg'
    output = options.output
    host = options.host
    sql = "SELECT layer, bgdi_flugjahr FROM meta_re2_wms_timestamps where layer not like 'ch.swisstopo.lubis-bildstreifen' order by 1,2"

    ################################
    # Ausgabe Variabeln
    ################################

    try:
        conn = psycopg2.connect("dbname='lubis' user='www-data' host='%s' password='www-data'" % host)
    except:
        print "ERROR: Unable to connect to the database host: %s" % host
        sys.exit(1)
    
    try:
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
    except:
        print "ERROR: Unable to perform query: %s " % sql
        sys.exit(1)
   
    years = set()
    layers = set()
    for row in rows:
        years.add(row[1])
        layers.add(row[0])
    
    # add new year to rows and years for latest timestamp containing all the data
    years.add('9999')
    for layer in layers:
        rows.append([layer,'9999'])

    if options.output == 'bash':
        # start generation of bash script content for tile generation
        output += "#! /bin/bash\n\n"
        for row in rows:
            output +="# Start testperimeter generation for layer %s - year %s ...\n" % (row[0],row[1])
            output += "buildout/bin/tilemanager -t 50 -c etc/ch.swisstopo.lubis/tilecache.swisstopo.lubis.%s.cfg %s -b 655000,194000,672500,206000\n" % (row[1],row[0])
            output +="\n# Start tile generation for layer %s - year %s ...\n" % (row[0],row[1])
            output += "buildout/bin/tilemanager -t 50 -c etc/ch.swisstopo.lubis/tilecache.swisstopo.lubis.%s.cfg %s\n" % (row[1],row[0])
            output +="\n\n"
        print output
    elif options.output == 'config':
        print "# Variablen output         = %s" % __file__
        print "# ------------------------------------------------------------------------------------------------"
        print "# template                 = %s" % template 
        print "#"
        print "# Skript Parameter: "
        print "# -o --output              = %s" % options.output
        print "# --host                   = %s" % options.host
        print "# ------------------------------------------------------------------------------------------------"
        print "#"
        # start generation of tilecache config
        if os.path.exists(template):
            for year in years:
                filename = template.replace('YYYY',str(year))
                print "Generiere tilecach config : %s ..." % filename
                shutil.copy2(template,filename)
                for line in fileinput.FileInput(filename, inplace=1):
                    line=line.replace("YYYY",str(year)).replace("WHERE bgdi_flugjahr = 9999","").replace("?time=9999","")
                    print line.strip()
            
