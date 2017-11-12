'''
Created on 24.10.2017

@author: bsmoehring
'''

import lxml.etree as ET
from lxml.etree import SubElement, Element, tostring
from constants import osm, jps, geometryAttribs
import jpsElements
from config import Config
import handler
import logging

def main():
    
    logging.info('Start')
    
    readOSM()
                  
    outgeometry = buildJPSTree()
    
    tree2xml(outgeometry)
    
    logging.info('operation finished!')

class Input:
    '''
    class to store the input-xml as tree and all nodes of this file separately as nodes
    '''
    logging.basicConfig(filename=Config().outputPath+'tes.log',level=logging.DEBUG)
    tree = ET.parse(Config().inputFile)
    nodes = {}
    for node in tree.iter(tag=osm.Node):
        key = node.attrib.get(osm.Id)
        nodes[key] = node 
    logging.info('Input loaded.') 

def readOSM():
    
    elements = {}
    for elem in Input.tree.iter():
        if elem.tag in [osm.Way, osm.Relation]:
            count = 0
            convert = False
            for tag in elem:
                k = tag.get(osm.Key)
                v = tag.get(osm.Value)
                try:
                    if v in Config.filterTags[k]:
                        convert = True
                except KeyError:
                    pass
                if tag.tag == osm.Member or tag.tag == osm.NodeRef:
                    count += 1
            if convert:
                try: 
                    elements[count].append(elem)
                except KeyError:
                    elements[count] = [elem]
    
    #sort list to start with largest elements
    eHandler = handler.ElementHandler()
    for count in sorted(elements.iterkeys(), reverse=True): 
        for elem in elements[count]:
            eHandler.handle(elem)  

def buildJPSTree():
    '''
    form an xml string from all geometry objects
    '''
    outGeometry = Element(jpsElements.Geometry().tag, geometryAttribs().attribs)
    outRooms = SubElement(outGeometry, jps.Rooms)
    for  room in jpsElements.Geometry().rooms:
        outRoom = SubElement(outRooms, room.tag, room.attribs)
        for subroom in room.subrooms:
            outSubroom = SubElement(outRoom, subroom.tag, subroom.attribs)
            for polygon in subroom.polygons:
                print polygon
                outPoly = SubElement(outSubroom, polygon.tag, polygon.attribs)
                for vertex in polygon.vertices:
                    outVertex = SubElement(outPoly, jps.Vertex, vertex.attribs)
                    #print vertex.attribs
       
    return outGeometry

def tree2xml(outGeometry):
    '''
    writes the ElementTree geometry to a xml file
    '''
    out = tostring(outGeometry, pretty_print=True)
    print out
    if Config.outputPath.endswith('.xml'):
        pass
    else:
        Config.outputPath += 'test.xml' 
    try:
        f = open(Config.outputPath, 'w')
        f.write(out)
        f.close()
    except Exception:
        print 'output not written!'
    
if      __name__ == "__main__":
    main()
