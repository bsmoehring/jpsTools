'''
Created on 11.11.2017

@author: bsmoehring
'''
from constants import osm, jps
from shapely import geometry, ops
from shapely.geometry.base import CAP_STYLE, JOIN_STYLE
from data import Output, Input
from xml.etree import ElementTree
import math, itertools
import copy
#from exceptions import UnhandleThisNodeException

class ElementHandler(object):
    '''
    classdocs
    '''
    def __init__(self, config):
        self.config = config
        self.elementsToHandle = Input.elementsToHandle
        self.nodes = Input.nodes
        self.nodePoints = {}
        for nodeId, node in self.nodes.items():
            self.nodePoints[nodeId] = geometry.Point(self.config.transform.WGS2XY(node))

    def runHandler(self):
    
        for osmId, elem in self.elementsToHandle.items():
            self.translateElem(osmId, elem)

        print('---')
        print(Output.usedNodes)
        print(Output.polygons)
        print(Output.elements)
        print(Output.wayNodes)
        
        '''
        handle all nodes that are part of more than 1 polygon and aren't tagged for unhandling:
        '''
        for nodeId, polyOsmIdLst in Output.usedNodes.items():
            try:
                self.handlePolysAroundNode(nodeId, list(polyOsmIdLst))
            except UnhandleThisNodeException:
                print(nodeId, 'not handled!')
        for nodeId, polyOsmIdLst in Output.usedNodes.items():
            try:
                self.getTransitionsForNode(nodeId, polyOsmIdLst)
            except UnhandleThisNodeException:
                pass
        
    def translateElem(self, osmId, elem):
        print('---')
        print(osmId)
        osmIds = []
        
        if elem.tag == osm.Way:
            #Way
            osmIds.append(osmId)
        elif elem.tag == osm.Relation:
            #Relation
            print('Element:', osmId, '--> Relation')
            for member in elem.iter(tag=osm.Member):
                if member.attrib[osm.Type] == osm.Way:
                    if member.attrib.get(osm.Role) == osm.Outer:
                        #outer member
                        print('Outer Member -> Way')
                        osmIds.append(member.attrib.get(osm.Ref))
                    elif member.attrib[osm.Role] == osm.Inner:
                        #inner member
                        print(member.attrib[osm.Ref], 'is an inner Member -> Not handled yet!')
                    else:
                        #no outer/inner
                        print(member.attrib[osm.Ref], 'is tagged: ', member.attrib[osm.Role], '--> no procedure implemented) yet.')
        if osmIds:
            for osmId in osmIds:
                poly = self.way2polygon(osmId)
                self.storeElement(osmId, elem, poly)

        else:
            print('Element:', osmId, 'is a:', elem.tag, '. How to handle this?')
            raise Exception
                
    def way2polygon(self, osmId):
        '''
        translate osm way to a shapely.geometry.polygon in order to to easily manipulate its shape.
        :param osmId:
        :return:
        '''
        print('element:', osmId, '--> Way')
        way = self.elementsToHandle[osmId]
        #get NodeRefs
        nodeRefs = []
        for child in way.iter(tag = osm.NodeRef):
            nodeRefs.append(child.attrib[osm.Ref])

        width = self.config.stanardWidth
        #search for specific Tags
        for child in way.iter(tag = osm.Tag):
            try:
                if child.attrib[osm.Key] == osm.Width:
                    width = float(child.attrib[osm.Value])
            except KeyError:
                pass

        XYList = self.config.transform.nodeRefs2XY(nodeRefs, self.nodes)

        #LineString
        print(way.attrib[osm.Id], 'is a LineString and needs to be buffered to create a Polygon.')
        ls = geometry.LineString(XYList)
        #polygon from linestring
        poly = ls.buffer(width/2, cap_style=CAP_STYLE.square, join_style=JOIN_STYLE.mitre, mitre_limit=width)
        
        return poly
    
    def defineExit(self, nodeId, polyOsmId):
        '''
        :param nodeId:
        :param polyOsmId:
        :return:
        '''
        print('---')
        print('exit for element ', polyOsmId, ' at ', nodeId)

        poly = Output.polygons[polyOsmId]
        b1, b2 = self.getBisectorPolygons(nodeId, polyOsmId, polyOsmId)
        poly = poly.difference(b1)
        poly = self.filterRelevantPoly(poly, polyOsmId)
        if isinstance(poly, geometry.Polygon):
            Output.polygons[polyOsmId] = poly
        self.getTransition(nodeId, polyOsmId, '-1', poly, b1)

    def handlePolysAroundNode(self, nodeId, polyOsmIdLst):
        '''
        defining how to handle all polygons around a specific node by their relation to each other.
        :param nodeId:
        :param polyOsmIdLst:
        :return:
        '''
        if len(polyOsmIdLst)==1 and self.isEndOfElement(nodeId, polyOsmIdLst[0]):
            return
            #self.defineExit(nodeId, polyOsmIdLst[0])
        elif len(polyOsmIdLst)<=1: return

        print('---')
        print('adjusting node', nodeId)
        print('polygons', polyOsmIdLst)
        self.checkNodeUnhandling(nodeId, polyOsmIdLst)

        union, unionCleared, unionAll = self.collectAdjustmentInformation(nodeId, polyOsmIdLst)
        for poly in [union, unionCleared, unionAll]:
            if not isinstance(poly, geometry.Polygon) or poly.is_empty:
                raise UnhandleThisNodeException
        '''
        handle if more than 2 elements related to point
        '''
        if len(polyOsmIdLst)>2:    
            '''
            buffer unionCleared by epsilon and differenciate other polygons
            '''
            self.adjustCaseMultiple(nodeId, polyOsmIdLst, unionCleared, unionAll)
                #transition = poly.intersection(Output.polygons[nodeId])
                #if transition.geom_type == shapely.LineString:
                #    transition = Output.Transition(transition, transition.coords[0], transition.coords[-1], osmId, nodeId)
                #    Output.transitionlst.append(transition)
        elif len(polyOsmIdLst)==2:
            osmId1 = polyOsmIdLst[0]
            osmId2 = polyOsmIdLst[1]
            poly1 = Output.polygons[osmId1]
            poly2 = Output.polygons[osmId2]
            #handle if 2 elements
            if self.isEndOfElement(nodeId, osmId1) and self.isEndOfElement(nodeId, osmId2):
                #both ends of line
                poly1, poly2 = self.adjustCaseEndEnd(nodeId, osmId1, osmId2, poly1, poly2)
            elif self.isEndOfElement(nodeId, osmId1):
                #one end of line
                poly2, poly1 = self.adjustCaseMidEnd(nodeId, osmId2, osmId1, poly2, poly1, union)
            elif self.isEndOfElement(nodeId, osmId2):
                #one end of line
                poly1, poly2 = self.adjustCaseMidEnd(nodeId, osmId1, osmId2, poly1, poly2, union)
            elif not self.isEndOfElement(nodeId, osmId1) and not self.isEndOfElement(nodeId, osmId2):
                #both middle points
                self.adjustCaseMultiple(nodeId, polyOsmIdLst, unionCleared, unionAll)
                return
            if isinstance(poly1, geometry.Polygon) and isinstance(poly2, geometry.Polygon):
                Output.polygons[osmId1] = poly1
                Output.polygons[osmId2] = poly2
            else:
                print(poly1)
                print(poly2)
                raise Exception
        else:
            print(polyOsmIdLst)
            raise Exception  
    
    def adjustCaseMultiple(self, nodeId, polyOsmIdLst, unionCleared, unionAll):
        '''
        adjusting a node with multiple ways by defining their intersection as a new polygon.
        then differenciating all polygons around the center polygon (unionCleared).
        if the handled node is in the middle of the element, the element is split into two seperate polygons.
        all references of the split polygon are updated in data.Output.
        :param nodeId:
        :param polyOsmIdLst:
        :param unionCleared:
        :param unionAll:
        :return:
        '''
        if not isinstance(unionCleared, geometry.Polygon) or unionCleared == None:
            print(nodeId, 'not handled')
            raise Exception
        newElem = ElementTree.Element(osm.Way, {osm.Id:str(nodeId), 'origin':'JPSTools'})
        ElementTree.SubElement(newElem, osm.Tag, {osm.Key:'highway', osm.Value:'footway'})
        ElementTree.SubElement(newElem, osm.Tag, {osm.Key:'area', osm.Value:'yes'})
        self.storeElement(nodeId, newElem, unionCleared, [nodeId])
        print('New Polygon', nodeId, 'created from', nodeId)
        
        for polyOsmId in polyOsmIdLst:
            poly = Output.polygons[polyOsmId]
            poly = poly.difference(unionCleared.buffer(self.config.bufferDistance))
            # difference only if poly is linked at end point
            print(polyOsmId)
            if not self.isEndOfElement(nodeId, polyOsmId):
                '''
                split poly by unionCleared. delete the old poly. add children as new polys. 
                '''
                print(poly)
                '''
                save nodeRefs when nodeId was reached and start a new List.
                '''
                nodeRefs = Output.wayNodes[polyOsmId]
                nodeRefsLst = []
                nodeRefsNew = []
                for nodeRef in nodeRefs:
                    nodeRefsNew.append(nodeRef)
                    if nodeRef == nodeId:
                        if len(nodeRefsNew)>1:
                            nodeRefsLst.append(nodeRefsNew)
                            nodeRefsNew = [nodeRef]
                if len(nodeRefsNew) > 1:
                    nodeRefsLst.append(nodeRefsNew)
                '''
                make LineStrings from nodeRefs
                '''
                if isinstance(poly, geometry.MultiPolygon):
                    i = 0
                    for polyChild in poly.geoms:
                        if not isinstance(polyChild, geometry.Polygon):
                            raise Exception
                        i += 1
                        newPolyId = polyOsmId + '0' + str(i)
                        #poly = self.fuseClosePoints(Output.polygons[nodeId], polyChild)
                        #poly = self.filterPolyPointsByDistance(unionAll, polyChild)
                        
                        '''
                        get relevant nodeRefs from nodeRefsLst
                        TODO: get largest intersection
                        '''
                        for nodeRefs in nodeRefsLst:
                            ls = geometry.LineString(self.config.transform.nodeRefs2XY(nodeRefs, self.nodes))
                            if isinstance(ls.intersection(polyChild), geometry.LineString):
                                elem = copy.deepcopy(Output.elements[polyOsmId])

                                self.storeElement(newPolyId, elem, polyChild, nodeRefs)
                                print(polyChild)
                                print('New Polygon', newPolyId, 'created from', polyOsmId)
                                break
                            
                    del Output.elements[polyOsmId]
                    del Output.polygons[polyOsmId]
                    del Output.wayNodes[polyOsmId]
                    Output.usedNodes[nodeId].remove(polyOsmId)
                    for key, osmIdWayLst in Output.usedNodes.items():
                        if polyOsmId in osmIdWayLst:
                            osmIdWayLst.remove(polyOsmId)
                else:
                    print(poly)
                    print(unionCleared)
                    #possible solution: split poly
                    raise Exception
            else:
                poly = self.filterRelevantPoly(poly, polyOsmId)
                poly = self.fuseClosePoints(Output.polygons[nodeId], poly)
                if poly.is_valid:
                    Output.polygons[polyOsmId] = poly
                else:
                    print(poly)
                    raise Exception
           
    def adjustCaseMidEnd(self, nodeId, osmIdMid, osmIdEnd, polyMid, polyEnd, union):
        '''
        returning two adjusted polygons. case T-junction.
        :param nodeId:
        :param osmIdMid:
        :param osmIdEnd:
        :param polyMid:
        :param polyEnd:
        :param union:
        :return:
        '''
        polyEnd = polyEnd.difference(polyMid)
        polyEnd = self.filterRelevantPoly(polyEnd, osmIdEnd)
        polyMid, polyEnd = self.mergePolys(osmIdMid, osmIdEnd, polyMid, polyEnd)
        return polyMid, polyEnd
    
    def adjustCaseEndEnd(self, nodeId, osmId1, osmId2, poly1, poly2):
        '''
        returning two adjusted polygons. case end-end-connection
        :param nodeId:
        :param osmId1:
        :param osmId2:
        :param poly1:
        :param poly2:
        :return:
        '''
        b1, b2 = self.getBisectorPolygons(nodeId, osmId1, osmId2)
        poly1 = poly1.difference(b2)
        poly1 = self.filterRelevantPoly(poly1, osmId1)
        poly2 = poly2.difference(b1)
        poly2 = self.filterRelevantPoly(poly2, osmId2)
        poly1, poly2 = self.mergePolys(osmId1, osmId2, poly1, poly2)
        return poly1, poly2
        
    def mergePolys(self, osmId1, osmId2, poly1, poly2):
        '''
        returning two polygons that should share the same coords at intersecting areas.
        union of the exterior LineString of Polygons. then filtering the closest Polygon.
        :param osmId1:
        :param osmId2:
        :param poly1:
        :param poly2:
        :return:
        '''
        lineString1 = geometry.LineString(list(poly1.buffer(self.config.bufferDistance).boundary.coords))
        lineString2 = geometry.LineString(list(poly2.buffer(self.config.bufferDistance).boundary.coords))
        boundaries = lineString1.union(lineString2)
        multipoly = geometry.MultiPolygon([geom for geom in ops.polygonize(boundaries)])
        poly1 = self.filterRelevantPoly(multipoly, osmId1)
        poly2 = self.filterRelevantPoly(multipoly, osmId2)
        unionAll = poly1.buffer(self.config.bufferDistance).union(poly2.buffer(self.config.bufferDistance))
        if not isinstance(unionAll, geometry.Polygon):
            raise Exception
        poly1 = self.filterPolyPointsByDistance(unionAll, poly1)
        poly2 = self.filterPolyPointsByDistance(unionAll, poly2)
        poly1 = self.fuseClosePoints(unionAll, poly1)
        poly2 = self.fuseClosePoints(unionAll, poly2)
        return poly1, poly2
        
    def collectAdjustmentInformation(self, nodeId, polyOsmIdLst = []):
        '''
        returns union, unionAll, unionCleared, polyEndInfo
        :param nodeId:
        :param polyOsmIdLst:
        :return:
        '''
        for osmId in polyOsmIdLst:
            if nodeId in Output.wayNodes[osmId]:
                pass
            else:
                raise Exception
        
        unionAll = geometry.Polygon()
        nodePoint = self.nodePoints[nodeId]
        
        for polyOsmId in polyOsmIdLst:
            unionAll = ops.unary_union([unionAll, Output.polygons[polyOsmId].buffer(self.config.bufferDistance)])
        if isinstance(unionAll, geometry.MultiPolygon) or isinstance(unionAll, geometry.GeometryCollection):
            for geom in unionAll.geoms:
                if nodePoint.within(geom.buffer(self.config.bufferDistance)):
                    unionAll = geom
                    break
        if not isinstance(unionAll, geometry.Polygon):
            print(nodeId, ' not handled')
            print(unionAll)
            raise UnhandleThisNodeException
        '''
        all combinations of polygons in poly
        if distance to unionAll is < epsilon -> use point for intersection poly
        '''
        polyintersects = []
        for polyOsmIdA, polyOsmIdB in itertools.combinations(polyOsmIdLst, 2):
            polyA = Output.polygons[polyOsmIdA]
            polyB = Output.polygons[polyOsmIdB]
            polyintersects.append(polyA.intersection(polyB))
        union = ops.cascaded_union(polyintersects)
        if isinstance(union, geometry.MultiPolygon) or isinstance(union, geometry.GeometryCollection):
            for geom in union.geoms:
                if isinstance(geom, geometry.Polygon) and nodePoint.within(geom.buffer(self.config.bufferDistance)):
                    union = geom
                    break
        if isinstance(union, geometry.Polygon):
            unionCleared = self.filterPolyPointsByDistance(unionAll, union)
        else:
            unionCleared = None
        
        return union, unionCleared, unionAll
    
    def storeElement(self, osmId, elem, poly, nodeRefs = []):
        '''
        storing references of the approved polygon in usedNodes{}, polygons{}, elements{} and wayNodes{}
        use the List nodeRefs instead of the elements tags if it's given
        :param osmId:
        :param elem:
        :param poly:
        :param nodeRefs:
        :return:
        '''

        if not isinstance(poly, geometry.Polygon) or poly.is_empty:
            raise Exception

        if nodeRefs:
            for elemChild in elem.findall(osm.NodeRef):
                elem.remove(elemChild)
            for nodeRef in nodeRefs:
                ElementTree.SubElement(elem, osm.NodeRef, {osm.Ref: nodeRef})

        Output().storeElement(osmId, elem, poly)
            
    def checkNodeUnhandling(self, nodeId, polyOsmIdLst):
        '''
        returns false if one of the nodes tags is in the unhandle dictionary
        :param nodeId:
        :param polyOsmIdLst:
        :return:
        '''
        node = self.nodes[nodeId]
        ok = True
        for tag in node.iter(tag = osm.Tag):
            try:
                if tag.attrib[osm.Value] in self.config.unhandleTag[tag.attrib[osm.Key]]:
                    ok = False
            except KeyError:
                pass
        if not ok:
            raise UnhandleThisNodeException
        
        for polyOsmId in polyOsmIdLst:
            area = False
            elem = Output.elements[polyOsmId]
            for tag in elem.iter(tag = osm.Tag):
                try:
                    if tag.attrib[osm.Value] in self.config.areaTags[tag.attrib[osm.Key]]:
                        area = True
                        break
                except KeyError:
                    pass
            if not area:
                return
        raise UnhandleThisNodeException
    
    def fuseClosePoints(self, polyStay, polyChange):
        '''
        moves the vertices of polyChange to vertices of PolyStay if their very close. solving numeric issues
        :param polyStay:
        :param polyChange:
        :return:
        '''
        polyExteriorLst = []
        for coord in polyChange.exterior.coords:
            p = geometry.Point(coord)
            changed = False
            for coord2 in polyStay.exterior.coords:
                p2 = geometry.Point(coord2)
                if p2.distance(p) < self.config.errorDistance:
                    polyExteriorLst.append(coord2)
                    changed = True
                    break
            if changed == False:
                polyExteriorLst.append(coord)
        poly = geometry.Polygon(polyExteriorLst)
        if isinstance(poly, geometry.Polygon) and poly.is_valid:
            return poly
        else:
            return polyChange
            print(poly)
            raise Exception     
    
    def filterPolyPointsByDistance(self, polyStay, polyChange): 
        '''
        returns the Polygon polyChange, cleared from points that aren't close to the outside of Polygon polyStay
        :param polyStay:
        :param polyChange:
        :return:
        '''
        if not isinstance(polyStay, geometry.Polygon) or not isinstance(polyChange, geometry.Polygon):
            print(polyStay)
            print(polyChange)
            raise Exception
        polyCleared = []
        for coord in polyChange.exterior.coords:
            p = geometry.Point(coord)
            if polyStay.exterior.distance(p) < self.config.errorDistance:
                polyCleared.append(coord)
        try:
            polyCleared = geometry.Polygon(polyCleared)
            return polyCleared
        except ValueError:
            return None
                
    def filterClosestPoly(self, polyOld, polyLst):
        '''
        return a poly of a list that is the closest in area to the polyOld
        TODO: filter list of polygons. returning each polygon with largest intersecting area
        :param polyOld:
        :param polyLst:
        :return:
        '''
        diff = float('inf')
        polyNew = polyOld
        for poly in polyLst:
            if abs(poly.area - polyOld.area)<diff:
                diff = abs(poly.area - polyOld.area)
                polyNew = poly
        return polyNew
            
    def filterRelevantPoly(self, multipoly, polyOsmId):
        '''
        if multipolygon:
        return Polygon with the longest intersection of the original element from given MultiPolygon.
        If no longest intersection:
        return largest polygon
        :param multipoly:
        :param polyOsmId:
        :return:
        '''
        if isinstance(multipoly, geometry.Polygon):
            return multipoly
        elif isinstance(multipoly, geometry.MultiPolygon):
            nodeRefs = Output.wayNodes[polyOsmId]
            ls = geometry.LineString(self.config.transform.nodeRefs2XY(nodeRefs, self.nodes))
            intersectionLength = 0
            longestIntersectionPoly = None
            for poly in multipoly.geoms:
                if ls.intersects(poly) and isinstance(poly, geometry.Polygon):
                    if ls.intersection(poly).length > intersectionLength:
                        intersectionLength = ls.intersection(poly).length
                        longestIntersectionPoly = poly
            if isinstance(longestIntersectionPoly, geometry.Polygon):
                return longestIntersectionPoly
        
            area = float("-infinity")
            for polygon in multipoly:
                if isinstance(polygon, geometry.Polygon) and polygon.area > area:
                    area = polygon.area
                    poly = polygon
        if isinstance(poly, geometry.Polygon):
            return poly
        else:
            raise Exception
    
    def isEndOfElement(self, nodeId, wayId):
        '''
        returns true of the node is an endpoint of way.
        rings/polygons might start and end at the same node. it is in this case not considered an endpoint.
        :param nodeId:
        :param wayId:
        :return:
        '''
        nodeRefs = Output.wayNodes[wayId]
        if nodeId == nodeRefs[0] or nodeId == nodeRefs[-1]:
                if nodeRefs[0] != nodeRefs[-1]:
                    return True
        elif nodeId in nodeRefs:
            return False
        else:
            raise Exception
        
    def getTransitionsForNode(self, nodeId, osmIdLst = []):
        '''
        :param nodeId:
        :param osmIdLst:
        :return:
        '''
        for pair in itertools.combinations(osmIdLst, 2):
            osmId1, osmId2 = pair[0], pair[1]
            poly1, poly2 = Output.polygons[osmId1], Output.polygons[osmId2]
            self.getTransition(nodeId, osmId1, osmId2, poly1, poly2)

    def getTransition(self, nodeId, osmId1, osmId2, poly1, poly2):

        transition = poly1.buffer(self.config.bufferDistance).intersection(poly2.buffer(self.config.bufferDistance))
        if isinstance(transition, geometry.base.BaseMultipartGeometry):
            distance = float("+infinity")
            for geom in transition.geoms:
                if isinstance(geom, geometry.Polygon) and geom.distance(self.nodePoints[nodeId]) < distance:
                    transition = geom
        if isinstance(transition, geometry.Polygon):
            unionAll = poly1.buffer(self.config.bufferDistance).union(poly2.buffer(self.config.bufferDistance))
            transition = self.filterPolyPointsByDistance(unionAll, transition)
            if isinstance(transition, geometry.Polygon):
                Output.transitionlst.append(Output.Transition(transition, osmId1, osmId2))
        else:
            return

    def getBisectorPolygons(self, nodeId, osmId1, osmId2):
        '''
        returning two polygons. Each of them is containing the two elements bisector as an line.
        Elements must share node nodeId.
        :param nodeId:
        :param osmId1:
        :param osmId2:
        :return:
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

        x0, y0 = self.config.transform.nodeRefs2XY(nodeId, self.nodes)
        x1, y1 = self.config.transform.nodeRefs2XY(node1, self.nodes)
        x2, y2 = self.config.transform.nodeRefs2XY(node2, self.nodes)

        vx1 = x1 - x0
        vy1 = y1 - y0
        vx2 = x2 - x0
        vy2 = y2 - y0

        v1len = math.sqrt(math.pow(vx1, 2) + math.pow(vy1, 2))
        v2len = math.sqrt(math.pow(vx2, 2) + math.pow(vy2, 2))

        vx1 = vx1 / v1len
        vy1 = vy1 / v1len
        vx2 = vx2 / v2len
        vy2 = vy2 / v2len

        t1 = math.atan2(vy1, vx1)
        t2 = math.atan2(vy2, vx2)
        t = (t1 + t2) / 2

        vx3 = math.cos(t)
        vy3 = math.sin(t)
        v3len = math.sqrt(math.pow(vx3, 2) + math.pow(vy3, 2))
        vx3 = vx3 / v3len
        vy3 = vy3 / v3len
        vx4 = -vx3
        vy4 = -vy3

        x1 = x0 + 0.1 * vx1
        y1 = y0 + 0.1 * vy1
        x2 = x0 + 0.1 * vx2
        y2 = y0 + 0.1 * vy2
        x3 = x0 + 5 * vx3
        y3 = y0 + 5 * vy3
        x4 = x0 + 5 * vx4
        y4 = y0 + 5 * vy4

        poly1 = geometry.Polygon([[x1, y1], [x3, y3], [x4, y4], [x1, y1]])
        poly2 = geometry.Polygon([[x2, y2], [x3, y3], [x4, y4], [x2, y2]])

        return poly1, poly2
        '''
        intersect = poly1.intersection(poly2)
        if isinstance(intersect, geometry.LineString):
            return poly1, poly2
        elif isinstance(intersect, geometry.Polygon):
            raise Exception
        '''

class UnhandleThisNodeException(Exception):
    pass
    
