from xml.etree import ElementTree as ET
from geometry import *
from jps_constants import *

def read_jps_geometry(filename):

    source = open(filename)
    tree = ET.parse(source)
    source.close()

    geo = Geometry()

    universe = Room(room_id='-1', caption='Universe')
    universe.addSubroom(Subroom(subroom_id='-1', jpsClass='Universe', ax=None, by=None, cz=None))
    geo.addRoom(universe)
    for room_et in tree.iter(tag=jps.Room):
        geo.addRoom(read_room(room_et))

    for transition_et in tree.iter(tag=jps.Transition):
        geo.addTransition(read_transition(transition_et))

    del geo.rooms['-1']
    return geo

def read_room(room_et = ET.Element):

    room_id = room_et.attrib[jps.Id]
    caption = room_et.attrib[jps.Caption]
    room_obj = Room(room_id, caption)

    for subroom in room_et.iter(tag=jps.Subroom):
        room_obj.addSubroom(read_subroom(subroom, room_id))

    for crossing_et in room_et.iter(tag=jps.Crossing):
        room_obj.addCrossing(read_crossing(crossing_et, room_id))

    return room_obj

def read_subroom(subroom_et = ET.Element, room_id = str):

    subroom_id = subroom_et.attrib[jps.Id]
    jpsClass = subroom_et.attrib[jps.Class]
    ax = subroom_et.attrib[jps.A_x]
    by = subroom_et.attrib[jps.B_y]
    cz = subroom_et.attrib[jps.C_z]
    upPX = upPY = upPZ = downPX = downPY = downPZ = None

    up_et = subroom_et.find(jps.Up)
    down_et = subroom_et.find(jps.Down)
    if up_et != None and down_et != None:
        vertex = read_vertex(up_et)
        upPX, upPY, upPZ = vertex.x, vertex.y, vertex.z
        vertex = read_vertex(down_et)
        downPX, downPY, downPZ = vertex.x, vertex.y, vertex.z

    subroom_obj = Subroom(subroom_id, jpsClass, ax, by, cz, upPX, upPY, upPZ, downPX, downPY, downPZ)

    for polygon in subroom_et.iter(tag=jps.Polygon):

        vertices = []

        for vertex in polygon.iter(tag=jps.Vertex):

            vertices.append(read_vertex(vertex))

        subroom_obj.addPolygon(Polygon(vertices), room_id)

    return subroom_obj

def read_crossing(crossing_et = ET.Element, room_id = str):

    crossing_id = crossing_et.attrib[jps.Id]
    subroom1_id = crossing_et.attrib[jps.Subroom1]
    subroom2_id = crossing_et.attrib[jps.Subroom2]
    vertices = []
    for vertex_et in crossing_et.iter(tag=jps.Vertex):
        vertices.append(read_vertex(vertex_et))

    return Crossing(crossing_id, vertices[0], vertices[1], subroom1_id, subroom2_id, room_id)

def read_transition(transition_et = ET.Element):

    transition_id = transition_et.attrib[jps.Id]
    room1_id = transition_et.attrib[jps.Room1]
    subroom1_id = transition_et.attrib[jps.Subroom1]
    room2_id = transition_et.attrib[jps.Room2]
    subroom2_id = transition_et.attrib[jps.Subroom2]
    caption = transition_et.attrib[jps.Caption]
    vertices = []
    for vertex_et in transition_et.iter(tag=jps.Vertex):
        vertices.append(read_vertex(vertex_et))

    return Transition(
        vertices[0], vertices[1], transition_id,  caption, 'NaN', room1_id, subroom1_id, room2_id, subroom2_id
    )


def read_vertex(vertex = ET.Element):

    x = float(vertex.attrib[jps.PX])
    y = float(vertex.attrib[jps.PY])
    z = None
    if jps.PZ in vertex.attrib:
        z = float(vertex.attrib[jps.PZ])

    return Vertex(x, y, z)



