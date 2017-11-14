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
    
    def __init__(self, bounds):
        
        minlat = float(bounds.attrib.get(osm.MinLat))
        minlon = float(bounds.attrib.get(osm.MinLon))
        self.minx, self.miny = self.projection(minlon, minlat) 
        print '---' 
        print 'Boundaries (reference point x,y=0,0):', self.minx, self.miny  
        
        
    def WGSToXY(self, lat, lon):
        
        x, y = self.projection(lon, lat)
        x -= self.minx
        y -= self.miny
        round(x, 2)
        round(y, 2)
        return x, y
        
        
        
        
        