'''
Created on 07.11.2017

@author: bsmoehring
'''
from pyproj import Proj
from constants import osm

class Transformation(object):
    '''
    classdocs
    '''                
    projection = Proj("+proj=utm +zone=32 +ellps=WGS84 +datum=WGS84 +units=m +no_defs ")  
    minx = 0
    miny = 0
    maxx = 0
    maxy = 0
    
    def __init__(self, bounds):
        
        minlat = float(bounds.attrib.get(osm.MinLat))
        minlon = float(bounds.attrib.get(osm.MinLon))
        minlat = float(bounds.attrib.get(osm.MaxLat))
        minlon = float(bounds.attrib.get(osm.MaxLon))
        self.minx, self.miny = self.projection(minlon, minlat) 
        print '---' 
        print 'Boundaries (reference point x,y=0,0):', self.minx, self.miny  
        
        
    def WGSToXY(self, node):
        
        x, y = self.projection(node.attrib[osm.Lon], node.attrib[osm.Lat])
        x -= self.minx
        y -= self.miny
        round(x, 2)
        round(y, 2)
        return x, y
    
    def nodeRefs2XY(self, nodeRefs, nodes):
        XYList = []
        for nodeRef in nodeRefs:
            try:
                node = nodes[nodeRef]
                x, y = self.WGSToXY(node)
                XYList.append((x, y))
            except KeyError:
                print nodeRef, 'is not in the nodes list. ->OSM inconsistency?'
        return XYList
        
        
        
        
        