'''
Created on 07.11.2017

@author: user
'''
from jpsConsistency import checkNeighbours, addNode
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
        checkNeighbours(room)
        self.rooms.append(room)
    
    def addTransition(self, transition):
        self.transitions.append(transition)
 
class Room:
    
    def __init__(self, id, level, caption):
        self.tag = jps.Room
        self.attribs = {}
        self.attribs[jps.Id] = str(len(Geometry().rooms))
        self.attribs[jps.OriginalId] = str(id)
        self.attribs['level'] = str(level)
        self.attribs[jps.Caption] = caption
        self.subrooms = []
    
    def addSubroom(self, subroom):
        self.subrooms.append(subroom)
        
    def getVertexes(self):
        vertexes = []
        for subroom in self.subrooms:
            for polygon in subroom.polygons:
                for vertex in polygon.vertexes:
                    vertexes.append(vertex)
        return vertexes
    
class Subroom:
    
    def __init__(self, id):
        self.tag = jps.Subroom
        self.polygons = []
        self.attribs = {}
        self.attribs['id'] = str(id)
        
    def addPolygon(self, p):
        self.polygons.append(p)
    
class Polygon:
    
    def __init__(self):
        self.tag = jps.Polygon
        self.attribs = {}
        self.attribs[jps.Caption] = jps.Wall
        self.vertexes = []
        
    def addVertex(self, vertex):
        self.vertexes.append(vertex)
    
class Vertex:
    
    def __init__(self, x, y, id):
        self.tag = jps.Vertex
        self.attribs = {}
        self.attribs[jps.PX] = x
        self.attribs[jps.PY] = y 
        self.attribs[jps.OriginalId] = id
        addNode(id)
        
    def getOriginalId(self):
        return self.attribs[jps.OriginalId]
