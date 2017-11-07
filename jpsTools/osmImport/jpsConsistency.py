'''
Created on 07.11.2017

@author: bsmoehring
'''
import jpsElements
from constants import jps

usedNodes = []
    
def addNode(id):
    usedNodes.append(id)

def checkNeighbours(room):
    '''
    checking if the vertexes of the newly added room are members of an already existing room
    '''
    newVertexList = []
    for vertex in room.getVertexes():
        newVertexList.append(vertex.getOriginalId())
    print newVertexList
