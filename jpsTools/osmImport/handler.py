'''
Created on 11.11.2017

@author: user
'''
from constants import osm
from config import Config
import shapely.geometry as geometry
from shapely.geometry.base import CAP_STYLE, JOIN_STYLE
from shapely import ops
from data import Output
import math, itertools
from numpy.core.fromnumeric import shape

class ElementHandler(object):
    '''
    classdocs
    '''
    def __init__(self, input, transform):
        self.tree = input.tree
        self.nodes = input.allNodes
        self.transform = transform
    
    def readOSM(self):
    
        elements = {}
        for elem in self.tree.iter():
            if elem.tag in [osm.Way, osm.Relation]:
                count = 0
                convert = False
                for tag in elem:
                    k = tag.get(osm.Key)
                    v = tag.get(osm.Value)
                    if k in Config.filterTags and v in Config.filterTags[k]:
                        convert = True
                if convert:
                    try: 
                        elements[count].append(elem)
                    except KeyError:
                        elements[count] = [elem]
        
        #sort list to start with largest elements
        for count in sorted(elements.iterkeys(), reverse=True): 
            for elem in elements[count]:
                poly = self.translate(elem)
                self.storeElement(elem, poly)
        #adjustpolys
        print '---'
        print Output.usedNodes
        print Output.polygons
        print Output.elements
        print Output.wayNodes
        for nodeId, polyOsmIdLst in Output.usedNodes.iteritems():
            if len(polyOsmIdLst) > 1:
                self.handlePolysAroundNode(nodeId, polyOsmIdLst)
                #self.checkConsistency(way, poly)
        #do transitions
        #=======================================================================
        # print '---'
        # for nodeId, osmIdLst in Output.transitionToDoLst.iteritems():
        #     for pair in itertools.combinations(osmIdLst, 2):
        #         osmId1, osmId2 = pair[0], pair[1]
        #         print osmId1, osmId2
        #         poly1, poly2 = Output.polygons[osmId1], Output.polygons[osmId2]
        #         self.getTransitions(nodeId, poly1, poly2, osmId1, osmId2)
        #=======================================================================
        
    def translate(self, elem):
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
                    return self.way2polygon(way, self.transform)
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
                poly = geometry.Polygon(XYList)
            else:
                #area == yes, but no polygon structure
                print  way.attrib[osm.Id], 'has wrong tags. Area=yes but first and last node references are not the same or less than 3 nodes'
                #continue as linestring?
        else:
            #LineString
            print way.attrib[osm.Id], 'is a LineString and needs to be buffered to create a Polygon.'
            ls = geometry.LineString(XYList)
            #polygon from linestring
            poly = ls.buffer(Config.stanardWidth/2, cap_style=CAP_STYLE.square, join_style=JOIN_STYLE.mitre, mitre_limit=Config.stanardWidth)
        
        return poly
    
    
    def handlePolysAroundNode(self, nodeId, polyOsmIdLst):
        '''
        defining how to handle all polygons around a specific node by their relation to each other.
        '''
        print'---'
        print 'adjusting node', nodeId
        print 'polygons', polyOsmIdLst
        
        polys = {}
        elems = {}
        polyEndInfo  = {}
        exteriors = {}
        for polyOsmId in polyOsmIdLst:
            polys[polyOsmId] = Output.polygons[polyOsmId]  
            elems[polyOsmId] = Output.elements[polyOsmId]   
            polyEndInfo[polyOsmId] = self.isEndOfElement(nodeId, polyOsmId)
            exteriors[polyOsmId] = geometry.LineString(polys[polyOsmId].exterior.coords)

        polyintersects = []
        intersectionPointLst = []
        #all combinations of polygons in poly
        for a, b in itertools.combinations(polyOsmIdLst, 2):
            #polygon intersections
            polyintersects.append(polys[a].intersection(polys[b]))
            #exterior intersections
            exIntersects = exteriors[a].intersection(exteriors[b])
            #get all point intersects of the polygons
            if isinstance(exIntersects, geometry.base.BaseMultipartGeometry):
                for p in exIntersects:
                    if isinstance(p, geometry.Point):
                        intersectionPointLst.append((p.x, p.y))
                    else:
                        print p
                        raise Exception
            elif isinstance(exIntersects, geometry.LineString):
                for p in exIntersects.coords:
                    intersectionPointLst.append(p)
            else:
                print intersectionPointLst
                print exIntersects
                raise Exception

        print 'intersectionPoints', intersectionPointLst
    
            #distance to the outside of the overall union of each point intersect
        union = ops.cascaded_union(polyintersects)
        unionAll = ops.cascaded_union(polys.values())
        unionCleared = []
        '''
        if distance to unionAll is < epsilon -> use point for intersection poly
        '''
        if isinstance(union, geometry.Polygon):
            for p in union.exterior.coords:
                p = geometry.Point(p[0], p[1])
                if unionAll.exterior.distance(p) < Config.errorDistance:
                    unionCleared.append((p.x, p.y))
            unionCleared = geometry.Polygon(unionCleared)
        elif isinstance(union, geometry.LineString):
            print 'not adjusting', nodeId
            return
        else: 
            print unionCleared
            raise Exception
        
        '''
        handle if more than 2 elements related to point
        '''
        if len(polyOsmIdLst)>2:    
            '''
            buffer unionCleared by epsilon and differenciate other polygons
            '''
            Output.polygons[nodeId] = unionCleared
            for osmId, poly in polys.iteritems():
                # difference only if poly is linked at end point
                if not polyEndInfo[osmId]:
                    print 'this case is not handled yet. more than 2 elements intersect but one of them in its center.'
                    #possible solution: not filtering relevant poly.
                    raise Exception
                poly = poly.difference(unionCleared.buffer(Config.errorDistance/5))
                poly = self.filterRelevantPoly(poly)
                poly = self.fuseClosePoints(unionCleared, poly)
                if poly.is_valid:
                    Output.polygons[osmId] = poly
                else:
                    print poly
                    raise Exception
                #transition = poly.intersection(unionCleared)
                #if transition.geom_type == shapely.LineString:
                #    transition = Output.Transition(transition, transition.coords[0], transition.coords[-1], osmId, nodeId)
                #    Output.transitionlst.append(transition)
        elif len(polyOsmIdLst)==2:
            osmId1 = polyOsmIdLst[0]
            osmId2 = polyOsmIdLst[1]
            poly1 = polys[osmId1]
            poly2 = polys[osmId2]
            #handle if 2 elements
            if polyEndInfo[osmId1] and polyEndInfo[osmId2]:
                #both ends of line
                b1, b2 = self.getBisectorPolygons(nodeId, osmId1, osmId2)
                poly1 = poly1.difference(b2)
                poly1 = self.filterRelevantPoly(poly1)
                poly2 = poly2.difference(b1)
                poly2 = self.filterRelevantPoly(poly2)
                poly2 = self.fuseClosePoints(poly1, poly2)
            elif polyEndInfo[osmId1]:
                #one end of line
                poly1 = poly1.difference(poly2)
                poly1 = self.filterRelevantPoly(poly1)
                poly1 = self.fuseClosePoints(poly2, poly1)
            elif polyEndInfo[osmId2]:
                #one end of line
                poly2 = poly2.difference(poly1)
                poly2 = self.filterRelevantPoly(poly2)
                poly2 = self.fuseClosePoints(poly1, poly2)
            elif not polyEndInfo[osmId1] and not polyEndInfo[osmId2]:
                #===============================================================
                # #like if more than 2 elements
                # poly1 = poly1.difference(unionCleared.buffer(Config.errorDistance/5))
                # poly2 = poly2.difference(unionCleared.buffer(Config.errorDistance/5))
                # Output.polygons[nodeId] = unionCleared
                # if isinstance(poly1, geometry.MultiPolygon) and isinstance(poly2, geometry.MultiPolygon):
                #     i = 1
                #     for poly in poly1:
                #         poly = self.fuseClosePoints(union, poly)
                #         Output.polygons[osmId1 + `000` + `i`] = poly
                #         i += 1
                #     i = 1
                #     for poly in poly2:
                #         poly = self.fuseClosePoints(union, poly)
                #         Output.polygons[osmId2 + `000` + `i`] = poly
                #         i += 1   
                #     return
                # else:
                #     print poly1
                #     print poly2
                #     raise Exception
                #===============================================================
                return
            if isinstance(poly1, geometry.Polygon) and isinstance(poly2, geometry.Polygon):
                Output.polygons[osmId1] = poly1
                Output.polygons[osmId2] = poly2
            else:
                print poly1
                print poly2
                raise Exception
            #===================================================================
            # transition = poly1.intersection(poly2)
            # if transition.geom_type == shapely.LineString:
            #     transition = Output.Transition(transition, transition.coords[0], transition.coords[-1], osmId1, osmId2)
            #     Output.transitionlst.append(transition) 
            # elif transition.geom_type == shapely.MultiLineString:
            #     #handle this
            #     pass
            # elif transition.geom_type == shapely.Point:
            #     pass
            # else: 
            #     print transition
            #     raise Exception 
            #===================================================================
        else:
            print polyOsmIdLst
            raise Exception  
            
    
    def getBisectorPolygons(self, nodeId, osmId1, osmId2):
        '''
        returning two polygons. Each of them is containing the two elements bisector as an line. 
        Elements must share node nodeId.
        '''
        nodeRefsNew = Output.wayNodes[osmId1]
        nodeRefsOld = Output.wayNodes[osmId2]
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
        
        poly1 = geometry.Polygon([[x1, y1], [x3, y3], [x4, y4], [x1, y1]])
        poly2 = geometry.Polygon([[x2, y2], [x3, y3], [x4, y4], [x2, y2]])
        
        print 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
        intersect = poly1.intersection(poly2)
        print intersect
        if isinstance(intersect, geometry.LineString):
            return poly1, poly2
        else:
            raise Exception
        
    def storeElement(self, elem, poly):
        '''
        storing references of the approved polygon in usedNodes{}, polygons{} and elements{}
        '''
        osmIdElem = elem.attrib[osm.Id]
        nodeRefs = []
        #parse nodes
        for nd in elem.iter(tag = osm.NodeRef):
            osmIdNode = nd.attrib[osm.Ref]
            nodeRefs.append(osmIdNode)
            node = self.nodes[osmIdNode]
            #unhandle Node if tag is in unhandleDictionary
            if self.checkNodeUnhandling(node):
                #add nodes and elemId to usedNodes
                if osmIdNode in Output.usedNodes:
                    #make sure that every node is added only once
                    if osmIdElem not in Output.usedNodes[osmIdNode]:
                        Output.usedNodes[osmIdNode].append(osmIdElem)
                    else:
                        pass
                else:
                    Output.usedNodes[osmIdNode] = [osmIdElem]
                
        Output.polygons[osmIdElem] = poly  
        Output.elements[osmIdElem] = elem 
        Output.wayNodes[osmIdElem] = nodeRefs
    
    def checkNodeUnhandling(self, node):
        '''
        returns false if one of the nodes tags is in the unhandle dictionary
        '''
        for tag in node.iter(tag = osm.Tag):
                try:
                    if tag.attrib[osm.Value] in Config.unhandleTag[tag.attrib[osm.Key]]:
                        return False
                except KeyError:
                    pass
        return True
                
    def fuseClosePoints(self, polyStay, polyChange):
        '''
        moves the vertices of polyChange to vertices of PolyStay if their very close. solving numeric issues
        '''
        polyExteriorLst = []
        for coord in polyChange.exterior.coords:
            p = geometry.Point(coord)
            changed = False
            for coord2 in polyStay.exterior.coords:
                p2 = geometry.Point(coord2)
                if p2.distance(p) < Config.errorDistance:
                    polyExteriorLst.append(coord2)
                    changed = True
                    break
            if changed == False:
                polyExteriorLst.append(coord)
        poly = geometry.Polygon(polyExteriorLst)
        if not poly.is_valid:
            print poly
        return poly       
                
    def filterClosestPolygon(self, polyOld, polyLst):
        '''
        return a poly of a list that is the closest in area to the polyOld
        '''
        diff = float('inf')
        polyNew = polyOld
        for poly in polyLst:
            if abs(poly.area - polyOld.area)<diff:
                diff = abs(poly.area - polyOld.area)
                polyNew = poly
        return polyNew
            
    def filterRelevantPoly(self, multipoly):
        '''
        return largest Polygon from given MultiP olygon.
        Method should later be optimized!
        '''    
        if isinstance(multipoly, geometry.Polygon):
            return multipoly
        
        polygons = [polygon for polygon in multipoly]
        area = 0
        
        for polygon in polygons:
            if polygon.area > area:
                area = polygon.area
                poly = polygon
        print poly.geom_type, 'retrieved from MultiPolygon because of its size.'
        return poly
    
    def isEndOfElement(self, nodeId, wayId):
        '''
        returns true of the node is an endpoint of way. 
        rings/polygons might start and end at the same node. it is in this case not considered an endpoint.
        '''
        nodeRefs = Output.wayNodes[wayId]
        if (nodeId == nodeRefs[0] or nodeId == nodeRefs[-1]) and nodeRefs[0] != nodeRefs[-1]:
            print nodeId, 'is the end of element', wayId
            end = True
        else:
            print nodeId, 'is somewhere in the middle of', wayId
            end = False
        return end
    
