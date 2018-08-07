from jps_constants import jps

class Geometry:
    tag = jps.Geometry
    rooms = {}
    transitions = {}

    def addRoom(self, room):
        '''
        adding a new room to the geometry container.
        cheking consistency and handling double-used nodes.
        '''
        self.rooms[room.attribs[jps.Id]] = room

    def addTransition(self, transition):
        '''

        :param transition:
        :return:
        '''
        assert isinstance(transition, Transition)
        transition_id = transition.attribs[jps.Id]
        self.transitions[transition_id] = transition

        room1 = transition.attribs[jps.Room1]
        subroom1 = transition.attribs[jps.Subroom1]
        room2 = transition.attribs[jps.Room2]
        subroom2 = transition.attribs[jps.Subroom2]
        self.rooms[room1].subrooms[subroom1].transition_ids.append(transition_id)
        self.rooms[room2].subrooms[subroom2].transition_ids.append(transition_id)

class Room:
    '''
    The geometry contains at least one room and one transition.
    Each room has a unique id, an optional caption and at least one subroom.
    Two rooms are separated by either walls or transitions./JuPedSim[2017]
    '''
    tag = jps.Room

    def __init__(self, room_id, caption='hall'):
        self.attribs = {}
        self.attribs[jps.Id] = room_id
        self.attribs[jps.Caption] = caption
        self.subrooms = {}
        self.crossings = {}

    def addSubroom(self, subroom):
        self.subrooms[subroom.attribs[jps.Id]] = subroom

    def getSubroomById(self, subroom_id):
        return self.subrooms[subroom_id]

    def addCrossing(self, crossing):
        self.crossings[crossing.attribs[jps.Id]] = crossing


class Subroom:
    '''
    Subrooms define the navigation mesh, i.e the walkable areas in the geometry.
    Each subroom is bounded by at least one crossing.JuPedSim[2017]
    Using standard-id 1 for subrooms so far. All rooms consist of a single subroom.
    '''
    tag = jps.Subroom

    def __init__(
            self, subroom_id, jpsClass, ax, by, cz,
            upPX=None, upPY=None, upPZ=None, downPX=None, downPY=None, downPZ=None
    ):
        self.polygons = []
        self.attribs = {}
        self.attribs[jps.Id] = subroom_id
        self.attribs[jps.Class] = jpsClass
        self.attribs[jps.A_x] = ax
        self.attribs[jps.B_y] = by
        self.attribs[jps.C_z] = cz
        self.upPX = upPX
        self.upPY = upPY
        self.upPZ = upPZ
        self.downPX = downPX
        self.downPY = downPY
        self.downPZ = downPZ
        self.obstacles = []
        self.transition_ids = []
        self.crossing_ids = []

    def addPolygon(self, p, room_id, nodeRefs=[]):
        if nodeRefs:
            if isinstance(p, Polygon) and len(p.vertices) == 2:
                for transition in Geometry.transitions.values():
                    if transition.attribs[jps.Room1] == room_id or transition.attribs[jps.Room2] == room_id:
                        if set(transition.nodeRefs) == set(nodeRefs):
                            return
                for crossing in Geometry.rooms[room_id].crossings.values():
                    if set(crossing.nodeRefs) == set(nodeRefs):
                        return
        self.polygons.append(p)

    def addObstacle(self, obstacle):
        self.obstacles.append(obstacle)


class Polygon:
    '''
    polygon describes the walls as a sequence of vertices. JuPedSim[2017]
    '''
    tag = jps.Polygon

    def __init__(self, vertices=[]):
        self.attribs = {}
        self.attribs[jps.Caption] = jps.Wall
        self.vertices = vertices


class Vertex:
    '''
    osm node. here as a point with x and y.
    additionally the osm.Id was added as originalId
    '''
    tag = jps.Vertex

    def __init__(self, x, y, z=None):
        self.attribs = {}
        self.x = x
        self.y = y
        self.z = z
        self.attribs[jps.PX] = str(round(self.x, 2))
        self.attribs[jps.PY] = str(round(self.y, 2))
        if z != None:
            self.attribs[jps.PZ] = str(round(self.z, 2))


class Transition:
    '''
    transition
    '''
    tag = jps.Transition

    def __init__(self, vertex_1, vertex_2, transition_id, caption, type, room1_id, subroom1_id,
                 room2_id, subroom2_id, nodeRefs=[]):
        self.id = id
        self.vertex1 = vertex_1
        self.vertex2 = vertex_2
        self.attribs = {}
        self.attribs[jps.Id] = transition_id
        self.attribs[jps.Caption] = caption
        self.attribs[jps.Type] = type
        self.attribs[jps.Room1] = room1_id
        self.attribs[jps.Subroom1] = subroom1_id
        self.attribs[jps.Room2] = room2_id
        self.attribs[jps.Subroom2] = subroom2_id
        self.nodeRefs = nodeRefs


class Crossing:
    '''

    '''
    tag = jps.Crossing

    def __init__(self, crossing_id, vertex_1, vertex_2, subroom1_id, subroom2_id, nodeRefs=[]):
        self.vertex1 = vertex_1
        self.vertex2 = vertex_2
        self.attribs = {}
        self.attribs[jps.Id] = crossing_id
        self.attribs[jps.Subroom1] = subroom1_id
        self.attribs[jps.Subroom2] = subroom2_id
        self.nodeRefs = nodeRefs

