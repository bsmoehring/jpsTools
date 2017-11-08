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
        usedVertexIds = jpsConsistency.checkNodeUseage(room)
        if not usedVertexIds:
            jpsConsistency.handleDoubleUseage(room, usedVertexIds)
        self.rooms.append(room)
        for vertex in room.getVertexes():
            jpsConsistency.addNode(vertex.attribs[jps.OriginalId])
    
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
    
    def __init__(self, id, level, caption):
        self.tag = jps.Room
        self.attribs = {}
        self.attribs[jps.Id] = str(len(Geometry().rooms))
        self.attribs[jps.OriginalId] = str(id)
        self.attribs['level'] = str(level)
        self.attribs[jps.Caption] = caption
        self.subrooms = {}
    
    def addSubroom(self, subroom):
        subroom.attribs[jps.Id] = str(len(self.subrooms))
        self.subrooms[subroom.attribs[jps.Id]] = subroom
        
    def getVertexes(self):
        vertexes = []
        for subroom in self.subrooms.itervalues():
            for polygon in subroom.polygons.itervalues():
                for vertex in polygon.vertexes.itervalues():
                    vertexes.append(vertex)
        return vertexes
    
class Subroom:
    '''
    Subrooms define the navigation mesh, i.e the walkable areas in the geometry.
    Each subroom is bounded by at least one crossing.JuPedSim[2017]
    '''
    
    def __init__(self):
        self.tag = jps.Subroom
        self.polygons = {}
        self.attribs = {}
        
    def addPolygon(self, p):
        p.attribs[jps.Id] = str(len(self.polygons))
        self.polygons[p.attribs[jps.Id]] = p
    
class Polygon:
    '''
    polygon describes the walls as a sequence of vertexes. JuPedSim[2017]
    '''
    
    
    def __init__(self):
        self.tag = jps.Polygon
        self.attribs = {}
        self.attribs[jps.Caption] = jps.Wall
        self.vertexes = {}
        
    def addVertex(self, vertex):
        self.vertexes[vertex.attribs[jps.OriginalId]] = vertex
    
class Vertex:
    '''
    osm node. here as a point with x and y. 
    additionally the osm.Id was added as originalId
    '''
    
    def __init__(self, x, y, id):
        self.tag = jps.Vertex
        self.attribs = {}
        self.attribs[jps.PX] = x
        self.attribs[jps.PY] = y 
        self.attribs[jps.OriginalId] = id
        
    def getOriginalId(self):
        return self.attribs[jps.OriginalId]
    
    def getNeighborVertexes(self):
        pass
