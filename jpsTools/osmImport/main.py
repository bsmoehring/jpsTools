'''
Created on 24.10.2017

@author: bsmoehring
'''

import xml.etree.ElementTree as ET
from xml.etree.ElementTree import SubElement, Element, tostring
from xml.dom import minidom
from constants import osm, jps, geometryAttribs
import jpsElements
import coords

outputPath = 'D:/Wichtiges/TUBerlin/Masterarbeit/Format_Conversions/'
inputPath = 'D:/Wichtiges/TUBerlin/Masterarbeit/Data/Alexanderplatz/Alexanderplatz.osm'

def main():
    
    coords.Transformation().setBounds(Input.tree.find(osm.Bounds))
    
    for elem in Input.tree.iter():
        if elem.tag in [osm.Way, osm.Relation]:
            for tag in elem:
                k = tag.get('k')
                v = tag.get('v')
                if k =='railway' and v =='platform':
                    print elem.tag, elem.attrib.get(osm.Id), tag.attrib
                    osm2jps(elem)
                elif (k =='public_transport' and v == 'station') or (k == 'railway' and v == 'station'):
                    osm2jps(elem)
                    
                  
    buildJpsXml()
            
    
     

class Input:
    '''
    class to store the input-xml as tree and all nodes of this file separately as nodes
    '''
    
    tree = ET.parse(inputPath)
    nodes = {}
    for node in tree.iter(tag=osm.Node):
        key = node.attrib.get(osm.Id)
        nodes[key] = node  
    
def osm2jps(elem):
    '''
    calling function to process element by its tag
    '''
    if elem.tag == osm.Way:
        way2jps(elem)
    if elem.tag == osm.Relation:
        for member in elem.iter(tag=osm.Member):
            if member.attrib.get(osm.Type) == osm.Way and member.attrib.get(osm.Role) == osm.Outer:
                id = member.attrib.get(osm.Ref)
                for way in Input.tree.iter(tag=osm.Way):
                    if way.attrib.get(osm.Id) == id:
                        way2jps(way)
    
def way2jps(elem):
    '''
    this method appends rooms as SubElements to the ElementTree geometry
    '''
    room = jpsElements.Room(elem.attrib.get(osm.Id), elem.attrib.get(osm.Level), 'hall')
    sroom = jpsElements.Subroom(len(room.subrooms))
    poly = jpsElements.Polygon()
    for nd in elem.iter(tag=osm.NodeRef):
        node = Input.nodes[nd.get(osm.Ref)]
        lat = node.attrib.get(osm.Lat)
        lon = node.attrib.get(osm.Lon)
        x, y = coords.Transformation().WGSToXY(lat, lon)
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
    outGeometry = Element(jps.Geometry, geometryAttribs().attribs)
    outRooms = SubElement(outGeometry, jps.Rooms)
    for  room in jpsElements.Geometry().rooms:
        outRoom = SubElement(outRooms, jps.Room, room.attribs)
        for subroom in room.subrooms:
            outSubroom = SubElement(outRoom, jps.Subroom, subroom.attribs)
            for polygon in subroom.polygons:
                outPoly = SubElement(outSubroom, jps.Polygon, polygon.attribs)
                for vertex in polygon.vertexes:
                    outVertex = SubElement(outPoly, jps.Vertex, vertex.attribs)
                    #print vertex.attribs
       
    geometry2jps(outGeometry, outputPath + 'test.xml')
       
    
def prettify(elem):
    '''
    Return a pretty-printed XML string for the Element.
    '''
    rough_string = tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def geometry2jps(outGeometry, outputFilename):
    '''
    writes the ElementTree geometry to a xml file
    '''
    out = prettify(outGeometry)
    print out
    if outputFilename.endswith('.xml'):
        pass
    else:
        outputFilename += '.xml' 
    f = open(outputFilename, 'w')
    f.write(out)
    f.close()
    
if __name__ == "__main__":
    main()
