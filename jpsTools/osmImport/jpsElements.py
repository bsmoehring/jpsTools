'''
Created on 07.11.2017

@author: bsmoehring
'''
from constants import jps, osm
from osmElements import OSMOut
from lxml.etree import SubElement, Element
from lxml.etree import tostring 

class JPSBuilder(object):
    
    def __init__(self, outputPath):
        self.translate2jps()
        outGeometry = self.buildJPSGEOtree()
        self.tree2xml(outGeometry, outputPath+'jps_geo.xml')
        outIni = self.buildJPSINItree()
        self.tree2xml(outIni, outputPath+'jps_ini.xml')
    
    def translate2jps(self):
        print ('---')
        for way in OSMOut.transitions:
            self.transition2jps(way)
        print ('---')
        for way in OSMOut.ways:
            self.way2jps(way)
        print('---')
        for way in OSMOut.goals:
            self.goal2jps(way)
                    
    def buildJPSGEOtree(self):
        '''
        form an xml string from all geometry objects
        '''
        print ('---')
        
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
            
        return outGeometry

    def way2jps(self, way):
        '''
        translate osm way to jps Elements with required attributes
        '''          
        jpsRoom = Room(way.attribs[osm.Id], way.tags[osm.Level])
        jpsSubroom = Subroom()
        index = 0
        while index < len(way.nodeRefs)-1:
            jpsVertex1 = Vertex(OSMOut.nodes[way.nodeRefs[index]].x, OSMOut.nodes[way.nodeRefs[index]].y)
            jpsVertex2 = Vertex(OSMOut.nodes[way.nodeRefs[index+1]].x, OSMOut.nodes[way.nodeRefs[index+1]].y)
            jpsWall = Polygon([jpsVertex1, jpsVertex2])
            jpsSubroom.addPolygon(jpsWall, [way.nodeRefs[index], way.nodeRefs[index+1]])
            index += 1
        jpsRoom.addSubroom(jpsSubroom)
        Geometry().addRoom(jpsRoom)
        
    def transition2jps(self, way):
        '''
        '''
        nodeRef1 = way.nodeRefs[0]
        nodeRef2 = way.nodeRefs[1]
        vertex1 = Vertex(OSMOut.nodes[nodeRef1].x, OSMOut.nodes[nodeRef1].y)
        vertex2 = Vertex(OSMOut.nodes[nodeRef2].x, OSMOut.nodes[nodeRef2].y)
        jpsTransition = Transition(vertex1, vertex2, len(Geometry.transitions), 'NaN', 'NaN', way.tags[jps.Room1], 0, way.tags[jps.Room2], 0, [nodeRef1, nodeRef2])
        Geometry().addTransition(jpsTransition)

    def goal2jps(self, way):
        '''
        translate osm way to jps Elements with required attributes
        '''
        vertices = []
        for nodeRef in way.nodeRefs:
            vertices.append(Vertex(OSMOut.nodes[nodeRef].x, OSMOut.nodes[nodeRef].y))
        IniFile().addGoal(Goal(vertices, way.tags))

    def buildJPSINItree(self):
        '''
        form an xml string from all geometry objects
        '''
        print('---')

        # required attributes of the geometry element
        attribs = {}
        attribs['version'] = '0.8'
        attribs['caption'] = 'second life'
        attribs['unit'] = 'm'
        # attribs['xml:nsxsi'] = 'http://www.w3.org/2001/XMLSchema-instance'
        # attribs['xsi:noNamespaceSchemaLocation'] = '../../xsd/jps_geometry.xsd'

        outIni = Element(IniFile().tag, attribs)
        outRouting = SubElement(outIni, 'routing')
        outGoals = SubElement(outRouting, 'goals')
        for goal in IniFile().goals:
            outGoal = SubElement(outGoals, 'goal', goal.attribs)
            for vertex in goal.vertices:
                SubElement(outGoal, jps.Vertex, vertex.attribs)
                # print vertex.attribs
        return outIni
    
    def tree2xml(self, tree, outputFile):
        '''
        writes the ElementTree geometry to a xml file
        '''
        out = tostring(tree, pretty_print=True,encoding='unicode')

        f = open(outputFile, 'w')
        f.write(out)
        f.close()
        print ('output written to %s' % outputFile)

class IniFile:
    tag = 'JuPedSim'
    goals = []

    def addGoal(self, goal):
        '''

        :param goal:
        :return:
        '''
        self.goals.append(goal)
            
class Geometry:
    tag = jps.Geometry 
    rooms = []
    transitions = []
    
    def addRoom(self, room):
        '''
        adding a new room to the geometry container.
        cheking consistency and handling double-used nodes.
        '''
        self.rooms.append(room)

    def addTransition(self, transition):
        self.transitions.append(transition)

    def getRoomByOriginalId(self, originalId):
        roomlst = []
        try:
            for room in self.rooms:
                if room.attribs[jps.OriginalId] == originalId:
                    roomlst.append(room)
            return roomlst
        except KeyError:
            print('no id:', id, 'in geometry.rooms[].')

class Room:
    '''
    The geometry contains at least one room and one transition.
    Each room has a unique id, an optional caption and at least one subroom.
    Two rooms are separated by either walls or transitions./JuPedSim[2017]
    '''
    tag = jps.Room
    
    def __init__(self, osmId, level, caption='hall'):
        self.attribs = {}
        self.attribs[jps.Id] = osmId
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
        self.attribs[jps.Class] = jps.Subroom
        
    def addPolygon(self, p, nodeRefs = []):
        if isinstance(p, Polygon) and len(p.vertices) == 2:
            for transition in Geometry.transitions:
                if set(transition.nodeRefs) == set(nodeRefs):
                    return
        self.polygons.append(p)
    
class Polygon:
    '''
    polygon describes the walls as a sequence of vertices. JuPedSim[2017]
    '''
    tag = jps.Polygon
    
    def __init__(self, vertices = []):
        self.attribs = {}
        self.attribs[jps.Caption] = jps.Wall
        self.vertices = vertices
    
class Vertex:
    '''
    osm node. here as a point with x and y. 
    additionally the osm.Id was added as originalId
    '''
    tag = jps.Vertex
    
    def __init__(self, x, y):
        self.attribs = {}
        self.x = str(round(x, 2))
        self.y = str(round(y, 2))        
        self.attribs[jps.PX] = self.x
        self.attribs[jps.PY] = self.y 
        
    def getOriginalId(self):
        return self.attribs[jps.OriginalId]
    
class Transition:
    '''
    transition
    '''
    tag = jps.Transition
    
    def __init__(self, vertex_1, vertex_2, id, caption, type, room1_id, subroom1_id, room2_id, subroom2_id, nodeRefs = []):
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
        self.nodeRefs = nodeRefs

class Goal:
    '''
    goal
    '''
    tag = jps.Goal

    def __init__(self, vertices = [], tags = {}):
        self.attribs = tags
        self.vertices = vertices
        
