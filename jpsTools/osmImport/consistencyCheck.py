'''
Created on 07.11.2017

@author: bsmoehring
'''
from constants import jps, osm
from shapely.geometry import Polygon, LineString

usedNodes = []
polygons = {}
    
def addNode(id):
    if id not in usedNodes:
        usedNodes.append(id)

def checkConsistency(poly, elem):
    
    pass

def checkNodeUseage(room):
    '''
    checking if the vertices of the newly added room are members of an already existing room.
    this is a quick check. 
    '''
    usedVertexIds = []
    for vertex in room.getvertices():
        id = vertex.getOriginalId()
        if id in usedNodes:
            print 'node:', id, 'is being used by multiple rooms.'
            usedVertexIds.append(id)
    return usedVertexIds

def handleDoubleUsage(nRoom, usedVertexIds):
    
    pass
    
     
    
    
    
        
        
        
        
        
        
        