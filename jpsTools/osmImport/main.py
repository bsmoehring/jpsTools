'''
Created on 24.10.2017

@author: bsmoehring
'''

import lxml.etree as ET
from lxml.etree import SubElement, Element, tostring
from constants import osm, jps, geometryAttribs
import jpsElements
from coords import Transformation
from config import Config
import logging

def main():
    
    logging.info('Start')
    
    t = Transformation(Input.tree.find(osm.Bounds))
    
    readOSM(t)
                  
    buildJpsXml()
    
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

def readOSM(t):
    
    elements = {}
    for elem in Input.tree.iter():
        if elem.tag in [osm.Way, osm.Relation]:
            count = 0
            convert = False
            for tag in elem:
                k = tag.get(osm.Key)
                v = tag.get(osm.Value)
                try:
                    if Config.tags[k] == v:
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
                #===============================================================
                # if k =='railway' and v =='platform':
                #     print elem.tag, elem.attrib.get(osm.Id), tag.attrib
                #===============================================================
                    
                #===============================================================
                # elif (k =='public_transport' and v == 'station') or (k == 'railway' and v == 'station'):
                #     osm2jps(elem)
                #===============================================================
    
    #sort list to start with largest elements
    for count in sorted(elements.iterkeys(), reverse=True): 
        for elem in elements[count]:
            osm2jps(elem, t)  
    
    
def osm2jps(elem, t):
    '''
    calling function to process element by its tag
    '''
    if elem.tag == osm.Way:
        way2jps(elem, t)
    if elem.tag == osm.Relation:
        for member in elem.iter(tag=osm.Member):
            if member.attrib.get(osm.Type) == osm.Way and member.attrib.get(osm.Role) == osm.Outer:
                id = member.attrib.get(osm.Ref)
                for way in Input.tree.iter(tag=osm.Way):
                    if way.attrib.get(osm.Id) == id:
                        way2jps(way, t)
    
def way2jps(elem, t):
    '''
    this method appends rooms as SubElements to the ElementTree geometry
    '''
    room = jpsElements.Room(elem.attrib.get(osm.Id), elem.attrib.get(osm.Level), 'hall')
    sroom = jpsElements.Subroom()
    poly = jpsElements.Polygon()
    for nd in elem.iter(tag=osm.NodeRef):
        node = Input.nodes[nd.get(osm.Ref)]
        lat = node.attrib.get(osm.Lat)
        lon = node.attrib.get(osm.Lon)
        x, y = t.WGSToXY(lat, lon)
        vert = jpsElements.Vertex(x, y, node.get(osm.Id))
        poly.addVertex(vert)
    sroom.addPolygon(poly)
    room.addSubroom(sroom)
    jpsElements.Geometry().addRoom(room)
    
def rel2jps(elem):
    '''
    determining how to process elements within the relation
    '''
    pass

def buildJpsXml():
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
       
    geometry2jps(outGeometry)

def geometry2jps(outGeometry):
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
