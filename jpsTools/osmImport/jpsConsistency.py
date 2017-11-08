'''
Created on 07.11.2017

@author: bsmoehring
'''
import jpsElements
from constants import jps

usedNodes = []
    
def addNode(id):
    if id not in usedNodes:
        usedNodes.append(id)

def checkNodeUseage(room):
    '''
    checking if the vertexes of the newly added room are members of an already existing room.
    this is a quick check. 
    '''
    usedVertexIds = []
    for vertex in room.getVertexes():
        id = vertex.getOriginalId()
        if id in usedNodes:
            print 'node:', id, 'is being used by multiple rooms.'
            usedVertexIds.append(id)
    return usedVertexIds

def handleDoubleUseage(nRoom, usedVertexIds):
    
    nRoomVertexCount = len(nRoom.getVertexes())
    
     
    for room in jpsElements.Geometry.rooms:
        dNodesCount = 0
        for vertex in room.getVertexes():
            if vertex.getOriginalId() in usedVertexIds:
                dNodesCount += 1
        if dNodesCount == 0:
            pass
        elif dNodesCount == 1:
            pass
        elif dNodesCount == 2:
            pass
        
        
        
        
        
        
        
        
        