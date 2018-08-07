from xml.etree.ElementTree import Element, SubElement, tostring
from jps_geometry import *

def buildJPSGEOtree(self, geometry):
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

    outGeometry = Element(geometry.tag, attribs)
    outRooms = SubElement(outGeometry, jps.Rooms)
    for room_id, room in geometry.rooms.items():
        outRoom = SubElement(outRooms, room.tag, room.attribs)
        for id, subroom in room.subrooms.items():
            outSubroom = SubElement(outRoom, subroom.tag, subroom.attribs)
            for polygon in subroom.polygons:
                outPoly = SubElement(outSubroom, polygon.tag, polygon.attribs)
                for vertex in polygon.vertices:
                    SubElement(outPoly, jps.Vertex, vertex.attribs)
                    # print vertex.attribs
            if subroom.attribs[jps.Class] == jps.Stair or subroom.attribs[jps.Class].startswith(jps.Escalator):
                SubElement(outSubroom, jps.Down,
                           {jps.PX: subroom.downPX, jps.PY: subroom.downPY, jps.PZ: subroom.downPZ})
                SubElement(outSubroom, jps.Up, {jps.PX: subroom.upPX, jps.PY: subroom.upPY, jps.PZ: subroom.upPZ})
            if subroom.obstacles:
                for obstacle in subroom.obstacles:
                    outObstacle = SubElement(outSubroom, jps.Obstacle, obstacle.attribs)
                    outPoly = SubElement(outObstacle, jps.Polygon)
                    for vertex in obstacle.vertices:
                        SubElement(outPoly, jps.Vertex, vertex.attribs)
        if room.crossings:
            outCrossings = SubElement(outRoom, jps.Crossings)
            for crossing in room.crossings:
                outCrossing = SubElement(outCrossings, crossing.tag, crossing.attribs)
                SubElement(outCrossing, jps.Vertex, crossing.vertex1.attribs)
                SubElement(outCrossing, jps.Vertex, crossing.vertex2.attribs)

    outTransitions = SubElement(outGeometry, jps.Transitions)
    for transition in geometry.transitions:
        outTransition = SubElement(outTransitions, jps.Transition, transition.attribs)
        SubElement(outTransition, jps.Vertex, transition.vertex1.attribs)
        SubElement(outTransition, jps.Vertex, transition.vertex2.attribs)

    return outGeometry

def tree2xml(self, tree, outputFile):
    '''
    writes the ElementTree geometry to a xml file
    '''
    out = tostring(tree, pretty_print=True,encoding='unicode')
    print(out)

    f = open(outputFile, 'w')
    f.write(out)
    f.close()
    print ('output written to %s' % outputFile)


