'''
Created on 07.11.2017

@author: user
'''
import jpsConsistency
from constants import jps

class Geometry:
    tag = jps.Geometry 
    rooms = []
    transitions = []
    
    
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
        try:
            for room in self.rooms:
                if room.attribs[jps.Id] == id:
                    return room
        except KeyError:
            print 'no id:'; id, 'in geometry.rooms[].'
 
class Room:
    '''
    The geometry contains at least one room and one transition.
    Each room has a unique id, an optional caption and at least one subroom.
    Two rooms are separated by either walls or transitions./JuPedSim[2017]
    '''
    tag = jps.Room
    
    def __init__(self, id, level, caption):
        self.attribs = {}
        self.attribs[jps.Id] = str(len(Geometry().rooms))
        self.attribs[jps.OriginalId] = id
        self.attribs['level'] = str(level)
        self.attribs[jps.Caption] = caption
        self.subrooms = []
    
    def addSubroom(self, subroom):
        subroom.attribs[jps.Id] = str(len(self.subrooms))
        self.subrooms.append(subroom)
        
    #===========================================================================
    # def getvertices(self):
    #     vertices = []
    #     for subroom in self.subrooms.itervalues():
    #         for polygon in subroom.polygons.itervalues():
    #             for vertexId in polygon.vertices:
    #                 vertices.append(Geometry.vertices[vertexId])
    #     return vertices
    #===========================================================================
    
class Subroom:
    '''
    Subrooms define the navigation mesh, i.e the walkable areas in the geometry.
    Each subroom is bounded by at least one crossing.JuPedSim[2017]
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
        self.attribs[jps.PX] = x
        self.attribs[jps.PY] = y 
        
    def getOriginalId(self):
        return self.attribs[jps.OriginalId]
    
class Transition:
    '''
    transition
    '''
    tag = jps.Transition
    
    def __init__(self, vertex_1, vertex_2, id, caption, type, room1_id, subroom1_id, room2_id, subroom2_id):
        self.vertices = []
        self.vertices.append(vertex_1)
        self.vertices.append(vertex_2)
        self.attribs = {}
        self.attribs[jps.Id] = id
        self.attribs[jps.Caption] = caption
        self.attribs[jps.Type] = type
        self.attribs[jps.Room1] = room1_id
        self.attribs[jps.Subroom1] = subroom1_id
        self.attribs[jps.Room2] = room2_id
        self.attribs[jps.Subroom2] = subroom2_id
        
    
    
