'''
Created on 07.11.2017

@author: bsmoehring
'''
from constants import jps, osm
import shapely.geometry as Geo
from input import Input
import copy

#osmId Node = [osmId Way]
usedNodes = {}
#osmId Way = polygon
polygons = {}
#osmId Way = Way/Element
elements = {}

def checkConsistency(elemNew, polyNew):
    '''
    iterates through elements nodes and checks if they're in use. 
    if yes, the polygon and counterpolygons (polygons that share the node) are adjusted.
    polygon information is then stored.
    '''
    usedNodeWays = {}
    for nd in elemNew.iter(tag = osm.NodeRef):
        nodeId = nd.attrib[osm.Ref]
        if nodeId in usedNodes:
            print nodeId, 'already in use!'
            for wayId in usedNodes[nodeId]:
                usedNodeWays[nodeId] = wayId
    
    #if len(wayIds) == 1:
    for nodeId, wayId in usedNodeWays.iteritems():
        polyOld = polygons[wayId]
        elemOld = elements[wayId]
        #poly = adjustPoly(nodeId, elemNew, polyNew, elemOld, polyOld)
    
    #approved
    #store osm nodes to usednodes   
    storeElement(elemNew, polyNew)
    
    return polyNew

def adjustPoly(nodeId, elemNew, polyNew, elemOld, polyOld):
    '''
    '''
    #end of line?
    #intersect = polyNew.intersection(polyOld)
    #Geo.Point( = Input.nodes[nodeId]
    
    print polyNew.intersects(polyOld)

def storeElement(elem, poly):
    '''
    storing references of the approved polygon in usedNodes{}, polygons{} and elements{}
    '''
    osmIdElem = elem.attrib[osm.Id]
    for nd in elem.iter(tag = osm.NodeRef):
        osmIdNode = nd.attrib[osm.Ref]
        if osmIdNode in usedNodes:
            usedNodes[osmIdNode].append(osmIdElem)
        else:
            usedNodes[osmIdNode] = [osmIdElem]
    polygons[osmIdElem] = poly  
    elements[osmIdElem] = elem 
    print poly, 'BBB' 

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

     
    
    
    
        
        
        
        
        
        
        