'''
Created on 11.11.2017

@author: user
'''
from constants import osm, shapely
from config import Config
from shapely import affinity, ops
from shapely.geometry import Polygon, LineString, GeometryCollection
from shapely.geometry.base import CAP_STYLE, JOIN_STYLE
from data import Output
import math

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
                    self.checkConsistency(way, poly, self.transform)
        else:
            print 'Element:', elem.attrib[osm.Id], 'is a:', elem.tag, '. How to handle this?'       
                
    def way2polygon(self, way, transform):
        '''
        translate osm way to a shapely.geometry.polygon in order to to easily manipulate its shape.
        '''
        print  'wayent:', way.attrib[osm.Id], '--> Way'
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
                polyNew = self.adjustPoly(nodeId, elemNew, polyNew, elemOld, polyOld, transform)
                self.getTransitions(polyNew, polyOld)
                print 'poly adjusted to: ', polyNew
        
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
            pNewCut, pOldCut = self.getBisector(nodeId, nodeRefsNew, nodeRefsOld)
            polyNew = polyNew.difference(pNewCut)
            polyOld = polyOld.difference(pOldCut)
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
                Output.polygons[elemOld.attrib[osm.Id]] = polyOld
        elif not newEnd and not oldEnd:
            polyNew = polyNew.difference(polyOld)
            
        return polyNew
    
    def getBisector(self, nodeId, nodeRefsNew, nodeRefsOld):
        '''
        returning the bisectrix of two connected elements
        '''
        self.transform.WGSToXY(self.nodes[nodeId])
        
        line = self.getEndVector(nodeId, nodeRefsNew, nodeRefsOld)
        
        x0 = list(line.coords)[1][0]
        y0 = list(line.coords)[1][1]
        x1 = list(line.coords)[0][0]
        y1 = list(line.coords)[0][1]
        x2 = list(line.coords)[2][0]
        y2 = list(line.coords)[2][1]
        
        vx1 = x1-x0
        vy1 = y1-y0
        vx2 = x2-x0
        vy2 = y2-y0
        
        t1 = math.atan2(vy1, vx1)
        t2 = math.atan2(vy2, vx2)
        
        v1len = math.sqrt(math.pow(vx1, 2) + math.pow(vy1, 2))
        v2len = math.sqrt(math.pow(vx2, 2) + math.pow(vy2, 2))
        
        vx1 = vx1/v1len
        vy1 = vy1/v1len
        vx2 = vx2/v2len
        vy2 = vy2/v2len
        
        print 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
        poly2 = Polygon([[x1, y1], [x0 + vx1 + vx2, y0 + vy1 + vy2], [x0 - vx1 - vx2, y0 - vy1 - vy2], [x1, y1]])
        poly1 = Polygon([[x2, y2], [x0 + vx1 + vx2, y0 + vy1 + vy2], [x0 - vx1 - vx2, y0 - vy1 - vy2], [x2, y2]])
        
        poly1 = affinity.scale(poly1, xfact=100.0, yfact=10.0, origin=(x0, y0))
        poly2 = affinity.scale(poly2, xfact=100.0, yfact=10.0, origin=(x0, y0))
        
        print poly1
        print poly2
        
        return poly1, poly2
        
        
    def getEndVector(self, nodeId, nodeRefsNew, nodeRefsOld):
        '''
        returns the Line Segment at the connecting end of an element
        '''
        line = []
        if nodeId == nodeRefsNew[0]:
            line.append(nodeRefsNew[1])
        elif nodeId == nodeRefsNew[-1]:
            line.append(nodeRefsNew[-2])
        else:
            Exception
        line.append(nodeId)
        if nodeId == nodeRefsOld[0]:
            line.append(nodeRefsOld[1])
        elif nodeId == nodeRefsOld[-1]:
            line.append(nodeRefsOld[-2])
        return LineString(self.transform.nodeRefs2XY(line, self.nodes))
        
        
    
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
    
    def getTransitions(self, polyNew, polyOld):
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
            
    def filterRelevantPoly(self, multipoly):
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
    

        
            
                