'''
Created on 07.11.2017

@author: user
'''
from constants import jps, osm, shapely
from data import Output
from shapely.geometry import LineString
from lxml.etree import SubElement, Element
from lxml.etree import tostring 

class JPSBuilder(object):
    
    def __init__(self, outputPath):
        self.translate2jps()
        self.buildJPSTree()
        self.tree2xml(outputPath)
    
    def translate2jps(self):
        print '---'
        for osmId, poly in Output.polygons.items():
            if poly.geom_type == shapely.Polygon:
                self.polygon2jps(osmId, poly)
            elif poly.geom_type == shapely.MultiPolygon:
                for polygon in poly:
                    self.polygon2jps(osmId, polygon)
        for transition in Output.transitionlst:
            self.transition2jps(transition)
                    
        self.buildJPSTree()      

    def buildJPSTree(self):
        '''
        form an xml string from all geometry objects
        '''
        print '---'
        
        #required attributes of the geometry element
        attribs = {}
        attribs['version'] = '0.8' 
        attribs['caption'] = 'second life' 
        attribs['unit'] = 'm'
        #attribs['xml:nsxsi'] = 'http://www.w3.org/2001/XMLSchema-instance'
        #attribs['xsi:noNamespaceSchemaLocation'] = '../../xsd/jps_geometry.xsd'
          
        outGeometry = Element(Geometry().tag, attribs)
        outRooms = SubElement(outGeometry, jps.Rooms)
        for  room in Geometry().rooms:
            outRoom = SubElement(outRooms, room.tag, room.attribs)
            for subroom in room.subrooms:
                outSubroom = SubElement(outRoom, subroom.tag, subroom.attribs)
                for polygon in subroom.polygons:
                    outPoly = SubElement(outSubroom, polygon.tag, polygon.attribs)
                    for vertex in polygon.vertices:
                        SubElement(outPoly, jps.Vertex, vertex.attribs)
                        #print vertex.attribs
        outTransitions = SubElement(outGeometry, jps.Transitions)
        for transition in Geometry().transitions:
            outTransition = SubElement(outTransitions, jps.Transition, transition.attribs)
            SubElement(outTransition, jps.Vertex, transition.vertex1.attribs)
            SubElement(outTransition, jps.Vertex, transition.vertex2.attribs)
            
        self.outGeometry = outGeometry

    def polygon2jps(self, osmId, poly):
        '''
        translate polygon to jps Elements with required attributes of the osm element
        '''          
        jpsRoom = Room(osmId, self.getLevel(osmId))
        jpsSubroom = Subroom()
        jpsPoly = Polygon()
        for coord in poly.exterior._get_coords():
            jpsVertex = Vertex(coord[0], coord[1])
            jpsPoly.addVertex(jpsVertex)
        jpsSubroom.addPolygon(jpsPoly)
        jpsRoom.addSubroom(jpsSubroom)
        Geometry().addRoom(jpsRoom)
        
    def transition2jps(self, transition):
        if transition.line.geom_type == shapely.LineString:
            vertex1 = Vertex(transition.coord1[0], transition.coord1[1])
            vertex2 = Vertex(transition.coord2[0], transition.coord2[1])
            jpsTransition = Transition(vertex1, vertex2, len(Geometry.transitions), 'NaN', 'NaN',
                                       Geometry.idOsmJps[transition.osmId1], 0, Geometry.idOsmJps[transition.osmId2], 0)
            Geometry().addTransition(jpsTransition)
        else:
            Exception
    
    def tree2xml(self, outputPath):
        '''
        writes the ElementTree geometry to a xml file
        '''
        out = tostring(self.outGeometry, pretty_print=True)
        print '---'
        #print out
        if outputPath.endswith('.xml'):
            pass
        else:
            outputPath += 'test.xml' 
        try:
            f = open(outputPath, 'w')
            f.write(out)
            f.close()
            print 'output written to', outputPath
        except Exception:
            print 'output not written!'
    
    def getLevel(self, osmId):
        try: 
            elem = Output.elements[osmId]
        except KeyError:
            return '0'
        for tag in elem.iter(tag=osm.Tag):
            if tag.attrib[osm.Key] == osm.Level:
                return tag.attrib[osm.Value]
        print elem.attrib[osm.Id], 'has no tag level. Returning standard 0'
        return '0'

class Geometry:
    tag = jps.Geometry 
    rooms = []
    transitions = []
    idOsmJps = {}
    
    
    #=======================================================================
    # def __init__(self):
    #     self.tag = 'geometry' 
    #     self.rooms = []
    #     self.transitions = []
    #=======================================================================
        
    def addRoom(self, room):
        '''
        adding a new room to the geometry container. 
        cheking consistency and handling double-used nodes.
        '''
        self.rooms.append(room)
    
    def addTransition(self, transition):
        self.transitions.append(transition)
        
    def getRoomById(self, id):
        roomlst = []
        try:
            for room in self.rooms:
                if room.attribs[jps.Id] == id:
                    roomlst.append(room)
            return roomlst
        except KeyError:
            print 'no id:'; id, 'in geometry.rooms[].'
            
    def getRoomByOriginalId(self, originalId):
        roomlst = []
        try:
            for room in self.rooms:
                if room.attribs[jps.OriginalId] == originalId:
                    roomlst.append(room)
            return roomlst
        except KeyError:
            print 'no id:'; id, 'in geometry.rooms[].'
 
class Room:
    '''
    The geometry contains at least one room and one transition.
    Each room has a unique id, an optional caption and at least one subroom.
    Two rooms are separated by either walls or transitions./JuPedSim[2017]
    '''
    tag = jps.Room
    
    def __init__(self, osmId, level, caption='hall'):
        self.attribs = {}
        jpsId = str(len(Geometry.rooms))
        Geometry.idOsmJps[osmId] = jpsId
        self.attribs[jps.Id] = jpsId
        self.attribs[jps.OriginalId] = osmId
        self.attribs['level'] = str(level)
        self.attribs[jps.Caption] = caption
        self.subrooms = []
    
    def addSubroom(self, subroom):
        subroom.attribs[jps.Id] = str(len(self.subrooms))
        self.subrooms.append(subroom)
    
class Subroom:
    '''
    Subrooms define the navigation mesh, i.e the walkable areas in the geometry.
    Each subroom is bounded by at least one crossing.JuPedSim[2017]
    Using standard-id 1 for subrooms so far. All rooms consist of a single subroom.
    '''
    tag = jps.Subroom
    
    def __init__(self, caption=''):
        self.polygons = []
        self.attribs = {}
        self.attribs[jps.Caption] = caption
        
    def addPolygon(self, p):
        p.attribs[jps.Id] = str(len(self.polygons))
        self.polygons.append(p)
    
class Polygon:
    '''
    polygon describes the walls as a sequence of vertices. JuPedSim[2017]
    '''
    tag = jps.Polygon
    
    def __init__(self):
        self.attribs = {}
        self.attribs[jps.Caption] = jps.Wall
        self.vertices = []
        
    def addVertex(self, vertex):
        self.vertices.append(vertex)
    
class Vertex:
    '''
    osm node. here as a point with x and y. 
    additionally the osm.Id was added as originalId
    '''
    tag = jps.Vertex
    
    def __init__(self, x, y):
        self.attribs = {}
        self.attribs[jps.PX] = str(x)
        self.attribs[jps.PY] = str(y) 
        
    def getOriginalId(self):
        return self.attribs[jps.OriginalId]
    
class Transition:
    '''
    transition
    '''
    tag = jps.Transition
    
    def __init__(self, vertex_1, vertex_2, id, caption, type, room1_id, subroom1_id, room2_id, subroom2_id):
        self.vertex1 = vertex_1
        self.vertex2 = vertex_2
        self.attribs = {}
        self.attribs[jps.Id] = str(id)
        self.attribs[jps.Caption] = caption
        self.attribs[jps.Type] = type
        self.attribs[jps.Room1] = room1_id
        self.attribs[jps.Subroom1] = str(subroom1_id)
        self.attribs[jps.Room2] = room2_id
        self.attribs[jps.Subroom2] = str(subroom2_id)
        
