#!/usr/bin/python
# -*- coding: latin-1 -*-

# Copyright (C) 2008 Chris Drexler
# All rights reserved.
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
# Author   : Chris Drexler <chris@drexler-family.com>


import xml.sax
import time
import re
import sys
import os
import getopt

from math import sqrt
from optparse import OptionParser

from string import replace, Template
from os import system 

g_options = None
g_inputfile = None
g_outputfile = None

def main(argv=None):
    global g_options,g_inputfile, g_outputfile

    if argv is None:
        argv = sys.argv

    usage   = '''usage: %prog [options] in.kml out.xml'''
    version = '''%prog 0.2'''

    parser = OptionParser(usage=usage, version=version)
    parser.set_defaults(verbose=True, execute=False, debug=False)
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true",
                      help="verbose output")
    parser.add_option("-q", "--quite", dest="verbose", action="store_false",
                      help="supress all output (quite)")
    parser.add_option("-l", "--level", dest="folder_level", metavar="", 
                      type="int", default=0,
                      help="folder level to be used for categories [default=%default]")
    parser.add_option("-m", "--mindist", dest="mindist", metavar="", 
                      type="float", default=0.0001,
                      help="minimun distance between two polyline points for the output xml file [default=%default]")
    parser.add_option("-d", "--debug", dest="debug", action="store_true",
                      help="enable debug output messages")
    (g_options, args) = parser.parse_args(argv[1:])

        
    if len(args) != 2:
        parser.print_help()
        return -1

    g_inputfile  = args[0]
    g_outputfile = args[1]

    if (g_options.debug):
        print g_inputfile, g_options

    handler = SampleHandler()
    parser = xml.sax.parse(open(args[0],"r"), handler)

    WriteXml(handler.folder_list, handler.placemark_list )


class SampleHandler(xml.sax.handler.ContentHandler):

    def __init__(self): 
        xml.sax.handler.ContentHandler.__init__(self)
        self.path = []
        self.path_content = []
        self.folders = []
        self.place_seqnr  = 0
        self.folder_seqnr = 0
        self.placemark = {}
        self.placemark_list = []
        self.folder_list = {}

        
    def startElement(self,name,attrs):
        #print "startElement: '%s'" % name
        self.path.append(name)
        self.path_content.append("")

        if  name == 'Placemark':
            self.placemark = {'id':self.place_seqnr, 
                              'cat':0, 
                              'name':"", 'desc':""}
            self.place_seqnr += 1

        if  name == 'Folder':
            self.folders.append({'id':self.folder_seqnr, 
                                 'name':"", 'desc':"", 'count':0})
            self.folder_seqnr += 1

    def characters(self,content):
        self.path_content[-1] += content

    def endElement(self,name):

        if len(self.path) >= 2:

            if  self.path[-2] == 'Folder' and self.path[-1] == 'name':
                self.folders[-1]['name'] = self.path_content[-1] 

            if  self.path[-2] == 'Folder' and self.path[-1] == 'description':
                self.folders[-1]['desc'] = self.path_content[-1] 

            if  self.path[-2] == 'Placemark' and self.path[-1] == 'name':
                self.placemark['name'] =  self.path_content[-1]

            if  self.path[-2] == 'Placemark' and self.path[-1] == 'description':
                self.placemark['desc'] =  self.path_content[-1]

        if len(self.path) >= 3:
            if  self.path[-3] == 'Placemark' and self.path[-2] == 'Point' and self.path[-1] == 'coordinates':
                m = re.search(r"([0-9.-]*),([0-9.-]*)",self.path_content[-1])
                self.placemark['lon'] =  m.group(1)
                self.placemark['lat'] =  m.group(2)
                self.placemark['type'] = "0"

            if  self.path[-3] == 'Placemark' and self.path[-2] == 'LineString' and self.path[-1] == 'coordinates':
                path = self.path_content[-1]
                self.placemark['type'] = "3"
                self.placemark['path'] =  []
                while path != "":
                    m = re.search(r"([0-9.-]*),([0-9.-]*),([0-9.-]*) +(.*)$",path)
                    mg = m.groups()
                    if len(mg) == 4:
                        path = mg[3]

                    self.placemark['path'].append( {'lon':mg[0], 'lat':mg[1]} )
                    #print mg[0],mg[1],mg[2]

                self.placemark['lon'] =  self.placemark['path'][0]['lon']
                self.placemark['lat'] =  self.placemark['path'][0]['lat']
                
        if  name == 'Folder':
                f = self.folders.pop()
                self.folder_list[f['id']] = f

        if  name == 'Placemark':
            try:
                self.placemark['cat'] = self.folders[g_options.folder_level]['id']
                self.folders[g_options.folder_level]['count'] +=1

            except:
                self.placemark['cat'] = self.folders[0]['id']
                self.folders[0]['count'] +=1

            if g_options.debug:
                print self.placemark
            self.placemark_list.append(self.placemark)
            #self.writeXml(self.folders[-1], self.placemark)

        self.path.pop()            
        self.path_content.pop()            

class WriteXml:
    def __init__ (self,folders,placemarks):
        self.myPlacemarks=placemarks
        self.myFolders = folders

        self.outfile = open(g_outputfile,'w')
        self.outfile.write('<?xml version="1.0" encoding="UTF-8" ?>\n<xml>\n'.encode("UTF-8"))
        self.writeFolders()
        self.writePlacemarks()

    def __del__(self):
        self.outfile.write('\n</xml>\n'.encode("UTF-8"))
        self.outfile.close()

    def writeFolders(self):
        category = Template(u'''<category id="$id" name="$name" title="$name" />\n''')
        for i in self.myFolders:
            if self.myFolders[i]['count'] > 0:
                self.outfile.write(category.substitute(self.myFolders[i]).encode("UTF-8"))
            
    def writePlacemarks(self):
        for placemark in self.myPlacemarks:
            point = Template(u'''
<info type="$type" id="$id" category="$cat" lat="$lat" lng="$lon">
  <name><![CDATA[$name]]></name>
  <address></address>
  <city></city>
  <state></state>
  <zipcode></zipcode>
  <country></country>\n''')

            pathstart = u'  <misc polycolor1="#F0F8FF" polycolor2="#4169E1" polyline="3">\n'
            pathentry = Template(u'    <point lat="$lat" lng="$lon" />\n')

            misc = Template(u'''  <misc><![CDATA[$desc]]></misc>\n''')

            self.outfile.write(point.substitute(placemark).encode("UTF-8") )
            if placemark['type'] == "3":
                self.outfile.write(pathstart.encode("UTF-8"))
                last_lat = 1000
                last_lon = 1000

                for i in placemark['path']:
                    if last_lat == 1000:
                        last_lat = float(i['lat'])
                        last_lon = float(i['lon'])
                        self.outfile.write(pathentry.substitute(i).encode("UTF-8"))
                    else:
                        cur_lat = float(i['lat'])
                        cur_lon = float(i['lon'])
                        dist = sqrt( (last_lat-cur_lat)**2+(last_lon-cur_lon)**2)
                        if dist > g_options.mindist:
                            last_lat = cur_lat
                            last_lon = cur_lon
                            self.outfile.write(pathentry.substitute(i).encode("UTF-8"))

                self.outfile.write('  </misc>\n'.encode("UTF-8"))
            else:
                self.outfile.write( misc.substitute(placemark).encode("UTF-8") )

                    
            self.outfile.write('</info>\n'.encode("UTF-8")) 

if __name__ == "__main__":
    sys.exit(main())

