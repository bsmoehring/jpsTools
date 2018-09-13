from constants import jps
from scipy.spatial import distance

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
        self.rooms[room1].subrooms[subroom1].transitions.append(transition)
        self.rooms[room2].subrooms[subroom2].transitions.append(transition)
        # self.rooms[room1].subrooms[subroom1].transition_ids.append(transition_id)
        # self.rooms[room2].subrooms[subroom2].transition_ids.append(transition_id)

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
        self.subrooms[subroom.attribs[jps.Subroom]] = subroom

    def getSubroomById(self, subroom_id):
        return self.subrooms[subroom_id]

    def addCrossing(self, crossing):
        self.crossings[crossing.attribs[jps.Id]] = crossing
        subroom1 = crossing.attribs[jps.Subroom1]
        subroom2 = crossing.attribs[jps.Subroom2]
        self.subrooms[subroom1].crossings.append(crossing)
        self.subrooms[subroom2].crossings.append(crossing)


class Subroom:
    '''
    Subrooms define the navigation mesh, i.e the walkable areas in the geometry.
    Each subroom is bounded by at least one crossing.JuPedSim[2017]
    Using standard-id 1 for subrooms so far. All rooms consist of a single subroom.
    '''
    tag = jps.Subroom

    def __init__(
            self, subroom_id, room_id, jpsClass, ax, by, cz,
            upPX=None, upPY=None, upPZ=None, downPX=None, downPY=None, downPZ=None
    ):
        self.polygons = []
        self.attribs = {}
        self.attribs[jps.Subroom] = subroom_id
        self.attribs[jps.Room] = room_id
        self.attribs[jps.Class] = jpsClass
        self.attribs[jps.A_x] = ax
        self.attribs[jps.B_y] = by
        self.attribs[jps.C_z] = cz
        self.up = {}
        if not None in [upPX, upPY, upPZ]:
            self.up[jps.PX] = str(upPX)
            self.up[jps.PY] = str(upPY)
            self.up[jps.PZ] = str(upPZ)
        self.down = {}
        if not None in [downPX, downPY, downPZ]:
            self.down[jps.PX] = str(downPX)
            self.down[jps.PY] = str(downPY)
            self.down[jps.PZ] = str(downPZ)
        self.obstacles = []
        self.transitions = []
        self.crossings = []

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

    def getNumOfTransCross(self):
        return len(self.transitions) + len(self.crossings)

    def getTransCrossLst(self, geo = Geometry):
        return self.crossings + self.transitions

    def getNeighbouringSubroomLst(self, geo = Geometry):
        neighbourLst = []
        for transition in self.transitions:
            subroom1 = geo.rooms[transition.attribs[jps.Room1]].subrooms[transition.attribs[jps.Subroom1]]
            subroom2 = geo.rooms[transition.attribs[jps.Room2]].subrooms[transition.attribs[jps.Subroom2]]
            if subroom1 != self:
                neighbourLst.append(subroom1)
            elif subroom2 != self:
                neighbourLst.append(subroom2)
        for crossing in self.crossings:
            subroom1 = geo.rooms[crossing.attribs[jps.Room]].subrooms[crossing.attribs[jps.Subroom1]]
            subroom2 = geo.rooms[crossing.attribs[jps.Room]].subrooms[crossing.attribs[jps.Subroom2]]
            if subroom1 != self:
                neighbourLst.append(subroom1)
            elif subroom2 != self:
                neighbourLst.append(subroom2)
        return neighbourLst

    def getShape4Sumo(self):
        shape = ''
        #append vertex if last vertex isn't the same
        for polygon in self.polygons:
            for vertex in polygon.vertices:
                assert isinstance(vertex, Vertex)
                coord = '%s,%s' % (vertex.x, vertex.y)
                if vertex.z != None:
                    coord += ','+str(vertex.z)
                if shape == '' or shape.split(' ')[-1] != coord:
                    if shape != '':
                        shape += ' '
                    shape += coord
        return shape

    def getCenterCoord(self):
        x_list = []
        y_list = []
        for polygon in self.polygons:
            [x_list.append(vertex.x) for vertex in polygon.vertices]
            [y_list.append(vertex.y) for vertex in polygon.vertices]
        xlength = len(x_list)
        ylength = len(y_list)
        x = round(sum(x_list) / xlength, 2)
        y = round(sum(y_list) / ylength, 2)
        return (x, y)

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

    def getCenterCoord(self):
        x = round((self.vertex1.x + self.vertex2.x)/2, 2)
        y = round((self.vertex1.y + self.vertex2.y)/2, 2)
        return (x, y)

    def getShape4Sumo(self, geo=Geometry):
        center_coord = self.getCenterCoord()
        half_width = self.getWidth()/2
        x_dif = (center_coord[0]-self.vertex1.x)/half_width/100
        y_dif = (center_coord[1]-self.vertex1.y)/half_width/100
        v_line = (x_dif, y_dif)
        v_perp = (v_line[1], -v_line[0])
        coord1 = (round(center_coord[0]+v_perp[0],2), round(center_coord[1]+v_perp[1],2))
        coord2 = (round(center_coord[0]-v_perp[0],2), round(center_coord[1]-v_perp[1],2))
        #check which coord is closer and append them to shape
        coord_subroom1 = geo.rooms[self.attribs[jps.Room1]].subrooms[self.attribs[jps.Subroom1]].getCenterCoord()
        if distance.euclidean(coord1, coord_subroom1)<distance.euclidean(coord2, coord_subroom1):
            shape = coord1+coord2
        else:
            shape = coord2+coord1
        return '%s,%s %s,%s' % shape

    def getWidth(self):
        a = (self.vertex1.x, self.vertex1.y)
        b = (self.vertex2.x, self.vertex2.y)
        width = round(distance.euclidean(a, b), 2)
        return width

class Crossing:
    '''

    '''
    tag = jps.Crossing

    def __init__(self, crossing_id, vertex_1, vertex_2, subroom1_id, subroom2_id, room_id, nodeRefs=[]):
        self.vertex1 = vertex_1
        self.vertex2 = vertex_2
        self.attribs = {}
        self.attribs[jps.Id] = crossing_id
        self.attribs[jps.Subroom1] = subroom1_id
        self.attribs[jps.Subroom2] = subroom2_id
        self.attribs[jps.Room] = room_id
        self.nodeRefs = nodeRefs

    def getCenterCoord(self):
        x = round((self.vertex1.x + self.vertex2.x)/2, 2)
        y = round((self.vertex1.y + self.vertex2.y)/2, 2)
        return (x, y)

    def getShape4Sumo(self, geo=Geometry):
        center_coord = self.getCenterCoord()
        half_width = self.getWidth()/2
        x_dif = (center_coord[0]-self.vertex1.x)/half_width/10
        y_dif = (center_coord[1]-self.vertex1.y)/half_width/10
        v_line = (x_dif, y_dif)
        v_perp = (v_line[1], -v_line[0])
        coord1 = (round(center_coord[0]+v_perp[0],2), round(center_coord[1]+v_perp[1],2))
        coord2 = (round(center_coord[0]-v_perp[0],2), round(center_coord[1]-v_perp[1],2))
        #check which coord is closer and append them to shape
        coord_subroom1 = geo.rooms[self.attribs[jps.Room]].subrooms[self.attribs[jps.Subroom1]].getCenterCoord()
        if distance.euclidean(coord1, coord_subroom1)<distance.euclidean(coord2, coord_subroom1):
            shape = coord1+coord2
        else:
            shape = coord2+coord1
        return '%s,%s %s,%s' % shape

    def getWidth(self):
        a = (self.vertex1.x, self.vertex1.y)
        b = (self.vertex2.x, self.vertex2.y)
        width = round(distance.euclidean(a, b), 2)
        return width