'''
Created on 07.11.2017

@author: bsmoehring
'''
from pyproj import Proj
from constants import osm
import sys

class Transformation(object):
    '''
    classdocs
    '''                
    projection = Proj("+proj=utm +zone=32 +ellps=WGS84 +datum=WGS84 +units=m +no_defs ")  
    minx = 0
    miny = 0
    maxx = 0
    maxy = 0
    
    def __init__(self, input):
        print '---' 
        try:
            bounds = input.tree.find(osm.Bounds)
            minlat = float(bounds.attrib.get(osm.MinLat))
            minlon = float(bounds.attrib.get(osm.MinLon))
            maxlat = float(bounds.attrib.get(osm.MaxLat))
            maxlon = float(bounds.attrib.get(osm.MaxLon))
        except (AttributeError):
            minlat, minlon = float('+inf'), float('+inf')
            maxlat, maxlon = float('-inf'), float('-inf')
            for node in input.tree.iter(tag=osm.Node):
                lat, lon = float(node.attrib[osm.Lat]), float(node.attrib[osm.Lon])
                if lat > maxlat:
                    maxlat = lat
                if lat < minlat:
                    minlat = lat
                if lon > maxlon:
                    maxlon = lon
                if lon < minlon:
                    minlon = lon
        self.minx, self.miny = self.projection(minlon, minlat) 
        self.maxx, self.maxy = self.projection(maxlon, maxlat) 
        print 'Boundaries (reference point x,y=0,0):', self.minx, self.miny  
        
        
    def WGSToXY(self, node):
        
        x, y = self.projection(node.attrib[osm.Lon], node.attrib[osm.Lat])
        x -= self.minx
        y -= self.miny
        round(x, 2)
        round(y, 2)
        return x, y
    
    def nodeRefs2XY(self, nodeRefs, nodes):
        if isinstance(nodeRefs, str):
            node = nodes[nodeRefs]
            x, y = self.WGSToXY(node)
            return x, y
        elif isinstance(nodeRefs, list):
            XYList = []
            for nodeRef in nodeRefs:
                try:
                    node = nodes[nodeRef]
                    x, y = self.WGSToXY(node)
                    XYList.append((x, y))
                except KeyError:
                    print nodeRef, 'is not in the nodes list. ->OSM inconsistency?'
            return XYList
        else:
            'Dont know how to handle this Element ', nodeRefs
        
        
        
        
        