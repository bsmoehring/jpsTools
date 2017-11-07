'''
Created on 07.11.2017

@author: bsmoehring
'''
import jpsElements
from constants import osm, jps, geometryAttribs

def checkNeighbours(room):
    '''
    checking if the vertexes of the newly added room are members of an already existing room
    '''
    newVertexList = []
    for subroom in room.subrooms:
        for polygon in subroom.polygons:
            for vertex in polygon.vertexes:
                newVertexList.append(vertex)
            
    for room in jpsElements.Geometry().rooms:
        for subroom in room.subrooms:
            for polygon in subroom.polygons:
                for vertex in polygon.vertexes:
                    if vertex.osmId in newVertexList:
                        print room.attribs.get(jps.Id), subroom.attribs.get(jps.Id), \
                        polygon.attribs.get(jps.Id), vertex.osmId 