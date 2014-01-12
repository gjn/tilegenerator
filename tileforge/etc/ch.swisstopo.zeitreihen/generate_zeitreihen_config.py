#!/usr/bin/env python
# coding=utf-8
#******************************************************************************
# 
#  Name:     generate_zeitreihen_config.py
#  Project:  BGDI Zeitreihen
#  Purpose:  Utility to create tilecache cfg files for requested years
#  Author:   Clausen Marcel
# 
#******************************************************************************
#  
#  Verwendung/Zweck:
#  + Benutzt config template tilecache.swisstopo.zeitreihen.YYYY.cfg
#  + generiert aus dem template tilecache.cfg Dateien für die gewünschten Jahre
#  
#******************************************************************************

import os,glob,sys,optparse,shutil,fileinput
from optparse import OptionParser

if __name__ == '__main__':
    ################################
    # Variablen
    ################################
    template = 'tilecache.swisstopo.zeitreihen.YYYY.cfg'
    output = ''
    
    ################################
    # Command Line Argument Parsing
    ################################

    epilog = """Examples:
    Beispiel 1: generiere tilecache Config von 1850 bis 1900:
    python generate_zeitreihen_config.py -f 1850 -t 1900
    
    Beispiel 2: Generiere ein bash Script zur Tilegenerierung
    python generate_zeitreihen_config.py -f 1850 -t 1900 -l ch.swisstopo.hiks-dufour.zeitreihen
    \n"""

    OptionParser.format_epilog = lambda self, formatter: self.epilog
    parser = OptionParser(epilog=epilog)
    parser.add_option("-f","--year_from", dest="year_from", 
                  help="Year Start")
    parser.add_option("-t","--year_to", dest="year_to", 
                  help="Year End")
    parser.add_option("-l","--layer", dest="layer", 
                  help="Comma separated list of Layer names, generate bash script tile generartion of years -f -t")    
    (options, args) = parser.parse_args()
    
    # -f is mandatory
    if options.year_from == None:
        parser.print_help()
        sys.exit( 1 )

    # -t is mandatory
    if options.year_to == None:
        parser.print_help()
        sys.exit( 1 )

    ################################
    # Ausgabe Variabeln
    ################################
    year_from = int(options.year_from)
    year_to = int(options.year_to)+1

    if options.layer:
        # start generation of bash script content for tile generation
        output += "#! /bin/bash\n\n"
        for layer in options.layer.split(","):
            output +="# Start testperimeter generation for layer %s ...\n" % layer
            for year in range(year_from,year_to):
                output += "buildout/bin/tilemanager -t 50 -c etc/ch.swisstopo.zeitreihen/tilecache.swisstopo.zeitreihen.%s.cfg %s -b 655000,194000,672500,206000\n" % (year,layer)
            output +="\n# Start tile generation for layer %s ...\n" % layer
            for year in range(year_from,year_to):
                output += "buildout/bin/tilemanager -t 50 -c etc/ch.swisstopo.zeitreihen/tilecache.swisstopo.zeitreihen.%s.cfg %s\n" % (year,layer)
            output +="\n\n"
        print output

    else:
        print "Variablen"
        print "------------------------------------------------------------------------------------------------"
        print "template                 = %s" % template 
        print ""
        print "Skript Parameter: "
        print "-f --year_from           = %s" % options.year_from
        print "-t --year_to             = %s" % options.year_to
        print "-l --layer               = %s" % options.layer
        print "------------------------------------------------------------------------------------------------"
        print ""
        # start generation of tilecache config
        if os.path.exists(template):
            for year in range(year_from,year_to):
                filename = template.replace('YYYY',str(year))
                print "Generiere tilecach config : %s ..." % filename
                shutil.copy2(template,filename)
                for line in fileinput.FileInput(filename, inplace=1):
                    line=line.replace("YYYY",str(year))
                    print line
            
