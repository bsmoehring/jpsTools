'''
Created on 07.11.2017

@author: bsmoehring
'''
from constants import osm, shapely
from shapely.geometry import Point, Polygon, MultiPolygon, LineString

#osmId Node = [osmId Way]
usedNodes = {}
#osmId Way = polygon
polygons = {}
#osmId Way = Way/Element
elements = {}
#osmId Way = [osmId Node]
wayNodes = {}
#osmId way = [polygon]
polygonTrash = {}
#transition
transitions = {}

def checkConsistency(elemNew, polyNew, transform):
    '''
    iterates through elements nodes and checks if they're in use. 
    if yes, the polygon and counterpolygons (polygons that share the node) are adjusted.
    polygon information is then stored.
    '''
    used = []
    for nd in elemNew.iter(tag = osm.NodeRef):
        nodeId = nd.attrib[osm.Ref]
        if nodeId not in used:
            if nodeId in usedNodes:
                print nodeId, 'already in use by elements: ', usedNodes[nodeId]
                used.append(nodeId)
    
    #if len(wayIds) == 1:
    for nodeId in used:
        for wayId in usedNodes[nodeId]:
            polyOld = polygons[wayId]
            elemOld = elements[wayId]
            polyNew = adjustPoly(nodeId, elemNew, polyNew, elemOld, polyOld, transform)
            getTransitions(polyNew, polyOld)
            print 'poly adjusted to: ', polyNew
    
    #approved
    #store osm nodes to usednodes   
    storeElement(elemNew, polyNew)
    
    return polyNew

def adjustPoly(nodeId, elemNew, polyNew, elemOld, polyOld, transform):
    '''
    '''
    
    if polyNew.disjoint(polyOld):
        print 'PROBLEM: polygons are supposed to be intersecting.'
    
    #end of line?
    nodeRefsOld = wayNodes[elemOld.attrib[osm.Id]]
    nodeRefsNew = []
    for nd in elemNew.iter(tag = osm.NodeRef):
        nodeRefsNew.append(nd.attrib[osm.Ref])
    if (nodeId == nodeRefsOld[0] or nodeId == nodeRefsOld[-1]) and nodeRefsOld[0] != nodeRefsOld[-1]:
        print nodeId, 'is the end of element', elemOld.attrib[osm.Id]
        oldEnd = True
    else:
        print nodeId, 'is somewhere in the middle of', elemOld.attrib[osm.Id]
        oldEnd = False
    if (nodeId == nodeRefsNew[0] or nodeId == nodeRefsNew[-1]) and nodeRefsNew[0] != nodeRefsNew[-1]:
        print nodeId, 'is the end of element', elemNew.attrib[osm.Id]
        newEnd = True
    else:
        print nodeId, 'is somewhere in the middle of', elemNew.attrib[osm.Id]
        newEnd = False
        
    #intersect
    intersect = polyNew.intersection(polyOld)
    
    if newEnd and oldEnd:
        pass
    elif newEnd and not oldEnd:
        polyNew = polyNew.difference(polyOld)
        if polyNew.geom_type == shapely.MultiPolygon:
            polyNew = filterRelevantPoly(polyNew)
    elif not newEnd and oldEnd:
        polyOld = polyOld.difference(polyNew)
        if polyOld.geom_type == shapely.MultiPolygon:
            polyOld = filterRelevantPoly(polyOld)
            polygons[elemOld.attrib[osm.Id]] = polyOld
    elif not newEnd and not oldEnd:
        polyNew = polyNew.difference(polyOld)
        
    return polyNew

def storeElement(elem, poly):
    '''
    storing references of the approved polygon in usedNodes{}, polygons{} and elements{}
    '''
    osmIdElem = elem.attrib[osm.Id]
    nodeRefs = []
    for nd in elem.iter(tag = osm.NodeRef):
        osmIdNode = nd.attrib[osm.Ref]
        nodeRefs.append(osmIdNode)
        if osmIdNode in usedNodes:
            usedNodes[osmIdNode].append(osmIdElem)
        else:
            usedNodes[osmIdNode] = [osmIdElem]
            
    polygons[osmIdElem] = poly  
    elements[osmIdElem] = elem 
    wayNodes[osmIdElem] = nodeRefs

def checkNodeUseage(room):
    '''
    checking if the vertices of the newly added room are members of an already existing room.
    this is a quick check. 
    '''
    usedVertexIds = []
    for vertex in room.getvertices():
        originalId = vertex.getOriginalId()
        if originalId in usedNodes:
            print 'node:', id, 'is being used by multiple rooms.'
            usedVertexIds.append(id)
    return usedVertexIds

def getTransitions(polyNew, polyOld):
    '''
    TODO get Transitions from two polygons
    '''
    transition = polyNew.intersection(polyOld)
    if transition.geom_type == shapely.LineString:
        print shapely.Polygon
        print transition
    else: 
        print 'Other'
        print transition
        
def filterRelevantPoly(multipoly):
    '''
    return largest Polygon from given Multipolygon.
    Method should later be optimized!
    USE CROSSES INSTEAD!
    '''    
    polygons = [polygon for polygon in multipoly]
    area = 0
    
    for polygon in polygons:
        if polygon.area > area:
            area = polygon.area
            poly = polygon
    print poly.geom_type, 'retrieved from MultiPolygon because of its size.'
    return poly
    
    
    
        
        
        
        
        
        
        