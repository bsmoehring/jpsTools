'''
Created on 11.11.2017

@author: user
'''
from constants import osm, shapely
from config import Config
from shapely import affinity, ops
from shapely.geometry import Polygon, LineString, Point
from shapely.geometry.base import CAP_STYLE, JOIN_STYLE
from data import Output
import math
import numpy

class ElementHandler(object):
    '''
    classdocs
    '''
    def __init__(self, input, transform):
        self.tree = input.tree
        self.nodes = input.allNodes
        self.transform = transform
        
    def handle(self, elem):
        print '---'
        print elem.attrib[osm.Id]
        wayRefs = []
        
        if elem.tag == osm.Way:
            #Way
            wayRefs.append(elem.attrib[osm.Id])
        elif elem.tag == osm.Relation:
            #Relation
            print 'Element:', elem.attrib[osm.Id], '--> Relation'
            for member in elem.iter(tag=osm.Member):
                if member.attrib[osm.Type] == osm.Way:
                    if member.attrib.get(osm.Role) == osm.Outer:
                        #outer member
                        print 'Outer Member -> Way'
                        wayRefs.append(member.attrib.get(osm.Ref))
                    elif member.attrib[osm.Role] == osm.Inner:
                        #inner member
                        print member.attrib[osm.Ref], 'is an inner Member -> Not handled yet!'
                    else:
                        #no outer/inner
                        print member.attrib[osm.Ref], 'is tagged: ', member.attrib[osm.Role], '--> no procedure implemented yet.'
        if wayRefs:
            for way in self.tree.iter(tag=osm.Way):
                if way.attrib.get(osm.Id) in wayRefs:
                    poly = self.way2polygon(way, self.transform)
                    print poly
                    self.checkConsistency(way, poly, self.transform)
        else:
            print 'Element:', elem.attrib[osm.Id], 'is a:', elem.tag, '. How to handle this?'       
                
    def way2polygon(self, way, transform):
        '''
        translate osm way to a shapely.geometry.polygon in order to to easily manipulate its shape.
        '''
        print  'element:', way.attrib[osm.Id], '--> Way'
        #area?
        area = False
        nodeRefs = []
        for child in way:
            if child.tag == osm.Tag: 
                try:
                    if child.attrib[osm.Value] in Config.areaTags[child.attrib[osm.Key]]:
                        area = True
                except KeyError:
                    pass
            if child.tag == osm.NodeRef:
                nodeRefs.append(child.attrib[osm.Ref])  
        XYList = transform.nodeRefs2XY(nodeRefs, self.nodes)
        print 'NodeRefs:', nodeRefs
        print 'Coordinates:', XYList
        if area:
            #check if first and last nodes are the same
            if len(nodeRefs) > 2 and nodeRefs[0] == nodeRefs [-1]:
                #polygon
                poly = Polygon(XYList)
            else:
                #area == yes, but no polygon structure
                print  way.attrib[osm.Id], 'has wrong tags. Area=yes but first and last node references are not the same or less than 3 nodes'
                #continue as linestring?
        else:
            #LineString
            print way.attrib[osm.Id], 'is a LineString and needs to be buffered to create a Polygon.'
            ls = LineString(XYList)
            #polygon from linestring
            poly = ls.buffer(Config.stanardWidth/2, cap_style=CAP_STYLE.square, join_style=JOIN_STYLE.mitre, mitre_limit=Config.stanardWidth)
        
        return poly
    
    def checkConsistency(self, elemNew, polyNew, transform):
        '''
        iterates through elements nodes and checks if they're in use. 
        if yes, the polygon and counterpolygons (polygons that share the node) are adjusted.
        polygon information is then stored.
        '''
        
        used = []
        for nd in elemNew.iter(tag = osm.NodeRef):
            nodeId = nd.attrib[osm.Ref]
            if nodeId not in used:
                if nodeId in Output.usedNodes:
                    print nodeId, 'already in use by elements: ', Output.usedNodes[nodeId]
                    used.append(nodeId)
        
        #if len(wayIds) == 1:
        for nodeId in used:
            for wayId in Output.usedNodes[nodeId]:
                polyOld = Output.polygons[wayId]
                elemOld = Output.elements[wayId]
                polyNew, polyOld = self.adjustPoly(nodeId, elemNew, polyNew, elemOld, polyOld, transform)
                print 'poly adjusted to: ', polyNew
                self.getTransitions(nodeId, polyNew, polyOld, elemNew, elemOld)
                Output.polygons[elemOld.attrib[osm.Id]] = polyOld
        
        #approved
        #store osm nodes to usednodes   
        self.storeElement(elemNew, polyNew)
    
    def adjustPoly(self, nodeId, elemNew, polyNew, elemOld, polyOld, transform):
        '''
        '''
        
        if polyNew.disjoint(polyOld):
            print 'PROBLEM: polygons are supposed to be intersecting.'
        
        #end of line?
        nodeRefsOld = Output.wayNodes[elemOld.attrib[osm.Id]]
        nodeRefsNew = self.getNodeRefsFromElement(elemNew)
        newEnd, oldEnd = self.isEndOfElement(nodeId, nodeRefsNew, elemNew, nodeRefsOld, elemOld)
            
        #intersect
        intersect = polyNew.intersection(polyOld)
        
        if newEnd and oldEnd:
            pCutNew, pCutOld = self.getBisectorPolygons(nodeId, nodeRefsNew, nodeRefsOld)
            polyNew = polyNew.difference(pCutOld)
            polyOld = polyOld.difference(pCutNew)
            if polyNew.geom_type == shapely.MultiPolygon:
                polyNew = self.filterRelevantPoly(polyNew)
            if polyOld.geom_type == shapely.MultiPolygon:
                polyOld = self.filterRelevantPoly(polyOld)
        elif newEnd and not oldEnd:
            polyNew = polyNew.difference(polyOld)
            if polyNew.geom_type == shapely.MultiPolygon:
                polyNew = self.filterRelevantPoly(polyNew)
        elif not newEnd and oldEnd:
            polyOld = polyOld.difference(polyNew)
            if polyOld.geom_type == shapely.MultiPolygon:
                polyOld = self.filterRelevantPoly(polyOld)
        elif not newEnd and not oldEnd:
            print 'Polygons', elemNew.attrib[osm.Id], 'and', elemOld.attrib[osm.Id], 'are crossing each other. Not handling this.'
        
        return polyNew, polyOld
    
    def getBisectorPolygons(self, nodeId, nodeRefsNew, nodeRefsOld):
        '''
        returning two polygons. Each of them is containing the two elements bisector as an line. 
        Elements must share node nodeId.
        '''
        if nodeId == nodeRefsNew[0]:
            node1 = nodeRefsNew[1]
        elif nodeId == nodeRefsNew[-1]:
            node1 = nodeRefsNew[-2]
        if nodeId == nodeRefsOld[0]:
            node2 = nodeRefsOld[1]
        elif nodeId == nodeRefsOld[-1]:
            node2 = nodeRefsOld[-2]
        
        x0, y0 = self.transform.nodeRefs2XY(nodeId, self.nodes)
        x1, y1 = self.transform.nodeRefs2XY(node1, self.nodes)
        x2, y2 = self.transform.nodeRefs2XY(node2, self.nodes)
        
        print x1, y1, x2, y2
        
        vx1 = x1-x0
        vy1 = y1-y0
        vx2 = x2-x0
        vy2 = y2-y0
        
        v1len = math.sqrt(math.pow(vx1, 2) + math.pow(vy1, 2))
        v2len = math.sqrt(math.pow(vx2, 2) + math.pow(vy2, 2))
        
        vx1 = vx1/v1len
        vy1 = vy1/v1len
        vx2 = vx2/v2len
        vy2 = vy2/v2len
        
        t1 = math.atan2(vy1, vx1)
        t2 = math.atan2(vy2, vx2)
        t = (t1 + t2)/2
        
        vx3 = math.cos(t)
        vy3 = math.sin(t)
        v3len = math.sqrt(math.pow(vx3, 2) + math.pow(vy3, 2))
        vx3 = vx3/v3len
        vy3 = vy3/v3len
        vx4 = -vx3
        vy4 = -vy3
        
        x1 = x0 + 5*vx1
        y1 = y0 + 5*vy1
        x2 = x0 + 5*vx2
        y2 = y0 + 5*vy2
        x3 = x0 + 5*vx3
        y3 = y0 + 5*vy3
        x4 = x0 + 5*vx4
        y4 = y0 + 5*vy4
        
        poly1 = Polygon([[x1, y1], [x3, y3], [x0, y0], [x4, y4], [x1, y1]])
        poly2 = Polygon([[x2, y2], [x3, y3], [x0, y0], [x4, y4], [x2, y2]])

        return poly1, poly2
        
    def storeElement(self, elem, poly):
        '''
        storing references of the approved polygon in usedNodes{}, polygons{} and elements{}
        '''
        osmIdElem = elem.attrib[osm.Id]
        nodeRefs = []
        for nd in elem.iter(tag = osm.NodeRef):
            osmIdNode = nd.attrib[osm.Ref]
            nodeRefs.append(osmIdNode)
            if osmIdNode in Output.usedNodes:
                Output.usedNodes[osmIdNode].append(osmIdElem)
            else:
                Output.usedNodes[osmIdNode] = [osmIdElem]
                
        Output.polygons[osmIdElem] = poly  
        Output.elements[osmIdElem] = elem 
        Output.wayNodes[osmIdElem] = nodeRefs
    
    def checkNodeUseage(self, room):
        '''
        checking if the vertices of the newly added room are members of an already existing room.
        this is a quick check. 
        '''
        usedVertexIds = []
        for vertex in room.getvertices():
            originalId = vertex.getOriginalId()
            if originalId in Output.usedNodes:
                print 'node:', id, 'is being used by multiple rooms.'
                usedVertexIds.append(id)
        return usedVertexIds
    
    def getTransitions(self, nodeId, polyNew, polyOld, elemNew, elemOld):
        '''
        TODO get Transitions from two polygons
        '''
        line = polyNew.intersection(polyOld)
        if line.geom_type == shapely.LineString or line.geom_type == shapely.Polygon:
            #===================================================================
            # if len(line.coords) > 2:
            #     #TODO: What happens with the Polygons???
            #     line = LineString(line.coords[0], line.coords[-1])
            #===================================================================
            print 'Transition', line
            room1osmId = elemNew.attrib[osm.Id]
            room2osmId = elemOld.attrib[osm.Id]
            transition = Output.Transition(line, room1osmId, room2osmId)
            Output.transitionlst.append(transition)
        else: 
            print 'Other', line
            
    def filterRelevantPoly(self, multipoly):
        '''
        return largest Polygon from given MultiP olygon.
        Method should later be optimized!
        '''    
        polygons = [polygon for polygon in multipoly]
        area = 0
        
        for polygon in polygons:
            if polygon.area > area:
                area = polygon.area
                poly = polygon
        print poly.geom_type, 'retrieved from MultiPolygon because of its size.'
        return poly
    
    def isEndOfElement(self, nodeId, nodeRefsNew, elemNew, nodeRefsOld, elemOld):
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
        return newEnd, oldEnd
    
    def getNodeRefsFromElement(self, elem):
        nodeRefs = []
        for nd in elem.iter(tag = osm.NodeRef):
            nodeRefs.append(nd.attrib[osm.Ref])
        return nodeRefs
            
                