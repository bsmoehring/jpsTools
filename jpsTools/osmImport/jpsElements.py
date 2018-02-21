'''
Created on 07.11.2017

@author: bsmoehring
'''
from constants import jps, osm
from data import Output, Input
from lxml.etree import SubElement, Element
from lxml.etree import tostring 

class JPSBuilder(object):
    
    def __init__(self, outputPath):
        self.translate2jps()
        outGeometry = self.buildJPSGEOtree()
        self.tree2xml(outGeometry, outputPath+'jps_geo.xml')
        outIni = self.buildJPSINItree()
        self.tree2xml(outIni, outputPath+'jps_ini.xml')
    
    def translate2jps(self):
        print('---')
        for way in Output.transitionlst:
            self.transition2jps(way)
        print ('---')
        for room_id, subroomLst in Output.subroomDic.items():
            self.room2jps(room_id, subroomLst)
        print ('---')
        #for way in OSMOut.ways:
        #    self.way2jps(way)
        print('---')
        for goal in Output.goalLst:
            self.goal2jps(goal)
                    
    def buildJPSGEOtree(self):
        '''
        form an xml string from all geometry objects
        '''
        print ('---')
        
        #required attributes of the geometry element
        attribs = {}
        attribs['version'] = '0.8' 
        attribs['caption'] = 'second life' 
        attribs['unit'] = 'm'
        #attribs['xml:nsxsi'] = 'http://www.w3.org/2001/XMLSchema-instance'
        #attribs['xsi:noNamespaceSchemaLocation'] = '../../xsd/jps_geometry.xsd'
          
        outGeometry = Element(Geometry().tag, attribs)
        outRooms = SubElement(outGeometry, jps.Rooms)
        for  room_id, room in Geometry().rooms.items():
            outRoom = SubElement(outRooms, room.tag, room.attribs)
            for subroom in room.subrooms:
                outSubroom = SubElement(outRoom, subroom.tag, subroom.attribs)
                for polygon in subroom.polygons:
                    outPoly = SubElement(outSubroom, polygon.tag, polygon.attribs)
                    for vertex in polygon.vertices:
                        SubElement(outPoly, jps.Vertex, vertex.attribs)
                        #print vertex.attribs
            if room.crossings:
                outCrossings = SubElement(outRoom, jps.Crossings)
                for crossing in room.crossings:
                    outCrossing = SubElement(outCrossings, crossing.tag, crossing.attribs)
                    SubElement(outCrossing, jps.Vertex, crossing.vertex1.attribs)
                    SubElement(outCrossing, jps.Vertex, crossing.vertex2.attribs)

        outTransitions = SubElement(outGeometry, jps.Transitions)
        for transition in Geometry().transitions:
            outTransition = SubElement(outTransitions, jps.Transition, transition.attribs)
            SubElement(outTransition, jps.Vertex, transition.vertex1.attribs)
            SubElement(outTransition, jps.Vertex, transition.vertex2.attribs)
            
        return outGeometry

    #def way2jps(self, way):
    #    '''
    #    translate osm way to jps Elements with required attributes
    #    '''
    #    jpsRoom = Room(way.attribs[osm.Id])
    #    jpsSubroom = Subroom()
    #    index = 0
    #    while index < len(way.nodeRefs)-1:
    #        jpsVertex1 = Vertex(OSMOut.nodes[way.nodeRefs[index]].x, OSMOut.nodes[way.nodeRefs[index]].y)
    #        jpsVertex2 = Vertex(OSMOut.nodes[way.nodeRefs[index+1]].x, OSMOut.nodes[way.nodeRefs[index+1]].y)
    #        jpsWall = Polygon([jpsVertex1, jpsVertex2])
    #        jpsSubroom.addPolygon(jpsWall, way.attribs[osm.Id], [way.nodeRefs[index], way.nodeRefs[index+1]])
    #        index += 1
    #    jpsRoom.addSubroom(jpsSubroom)
    #    Geometry().addRoom(jpsRoom)

    def room2jps(self, room_id, subroomLst = []):
        '''

        :param room_id:
        :param subroomLst:
        :return:
        '''
        jpsRoom = Room(room_id)
        try:
            for crossing in Output.crossingDic[room_id]:
                jpsRoom.addCrossing(self.crossing2jps(crossing))
        except KeyError: pass
        Geometry().addRoom(room_id, jpsRoom)
        for subroom in subroomLst:
            jpsSubroom = Subroom(subroom.subroom_id, subroom.jpsClass, subroom.jpsCaption, subroom.jpsC_z)
            index = 0
            while index < len(subroom.nodeRefs) - 1:
                jpsVertex1 = Vertex(Input.nodes[subroom.nodeRefs[index]].attrib[jps.PX], Input.nodes[subroom.nodeRefs[index]].attrib[jps.PY])
                jpsVertex2 = Vertex(Input.nodes[subroom.nodeRefs[index + 1]].attrib[jps.PX], Input.nodes[subroom.nodeRefs[index + 1]].attrib[jps.PY])
                jpsWall = Polygon([jpsVertex1, jpsVertex2])
                jpsSubroom.addPolygon(jpsWall, room_id, [subroom.nodeRefs[index], subroom.nodeRefs[index + 1]])
                index += 1
            Geometry().rooms[room_id].addSubroom(jpsSubroom)

        
    def transition2jps(self, transition):
        '''
        '''
        nodeRef1 = transition.nodeRef1
        nodeRef2 = transition.nodeRef2
        vertex1 = Vertex(Input.nodes[nodeRef1].attrib[jps.PX], Input.nodes[nodeRef1].attrib[jps.PY])
        vertex2 = Vertex(Input.nodes[nodeRef2].attrib[jps.PX], Input.nodes[nodeRef2].attrib[jps.PY])
        transition_id = transition.transition_id
        jpsTransition = Transition(vertex1, vertex2, transition_id, 'NaN', 'NaN',
                                   transition.room1_id, transition.subroom1_id,
                                   transition.room2_id, transition.subroom2_id, [nodeRef1, nodeRef2])
        Geometry().addTransition(jpsTransition)
        IniFile().addTransition(jpsTransition)

    def crossing2jps(self, crossing):
        '''

        :param crossing:
        :return:
        '''
        nodeRef1 = crossing.nodeRefs[0]
        nodeRef2 = crossing.nodeRefs[1]
        vertex1 = Vertex(Input.nodes[nodeRef1].attrib[jps.PX], Input.nodes[nodeRef1].attrib[jps.PY])
        vertex2 = Vertex(Input.nodes[nodeRef2].attrib[jps.PX], Input.nodes[nodeRef2].attrib[jps.PY])
        jpsCrossing = Crossing(crossing_id=crossing.crossing_id, vertex_1=vertex1, vertex_2=vertex2,
                               subroom1_id=crossing.subroom1_id, subroom2_id=crossing.subroom2_id,
                               nodeRefs=[nodeRef1, nodeRef2])
        return jpsCrossing

    def goal2jps(self, goal):
        '''
        translate osm way to jps Elements with required attributes
        '''
        vertices = []
        for nodeRef in goal.nodeRefs:
            vertices.append(Vertex(Input.nodes[nodeRef].attrib[jps.PX], Input.nodes[nodeRef].attrib[jps.PY]))
        IniFile().addGoal(Goal(vertices, goal.tags))

    def buildJPSINItree(self):
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

        outIni = Element(IniFile().tag, attribs)
        outRouting = SubElement(outIni, 'routing')
        outGoals = SubElement(outRouting, 'goals')
        for goal in IniFile().goals:
            outGoal = SubElement(outGoals, 'goal', goal.attribs)
            outPolygon = SubElement(outGoal, jps.Polygon)
            for vertex in goal.vertices:
                SubElement(outPolygon, jps.Vertex, vertex.attribs)
                # print vertex.attribs
        outTrafficConstraints = SubElement(outIni, 'traffic_constraints')
        outDoors = SubElement(outTrafficConstraints, 'doors')
        for transition in IniFile().transitions:
            attribs = {}
            attribs['trans_id']=transition.attribs[jps.Id]
            attribs[jps.Caption]=transition.attribs[jps.Caption]
            attribs['state']='open'
            SubElement(outDoors, 'door', attribs)

        outAgents = SubElement(outIni, 'agents', {'operational_model_id':'3'})
        outAgentsDistribution = SubElement(outAgents, 'agents_distribution')
        group_id = 1
        for goalFrom in IniFile().goals:
            for goalTo in IniFile().goals:
                attribs = {}
                attribs['group_id'] = str(group_id)
                attribs['agent_parameter_id'] = '1'
                attribs[jps.Room_ID] = goalFrom.attribs[jps.Room_ID]
                attribs[jps.Subroom_ID] = goalFrom.attribs[jps.Subroom_ID]
                attribs['number'] = '1'
                attribs['router_id'] = '1'
                attribs['goal_id'] = goalTo.attribs[jps.Id]
                SubElement(outAgentsDistribution, 'group', attribs)
                group_id += 1

        return outIni
    
    def tree2xml(self, tree, outputFile):
        '''
        writes the ElementTree geometry to a xml file
        '''
        out = tostring(tree, pretty_print=True,encoding='unicode')

        f = open(outputFile, 'w')
        f.write(out)
        f.close()
        print ('output written to %s' % outputFile)

class IniFile:
    tag = 'JuPedSim'
    goals = []
    transitions = []

    def addGoal(self, goal):
        '''

        :param goal:
        :return:
        '''
        self.goals.append(goal)

    def addTransition(self, transition):
        '''

        :param transition:
        :return:
        '''
        self.transitions.append(transition)

class Geometry:
    tag = jps.Geometry 
    rooms = {}
    transitions = []
    
    def addRoom(self, room_id, room):
        '''
        adding a new room to the geometry container.
        cheking consistency and handling double-used nodes.
        '''
        self.rooms[room_id]=room

    def addTransition(self, transition):
        self.transitions.append(transition)

class Room:
    '''
    The geometry contains at least one room and one transition.
    Each room has a unique id, an optional caption and at least one subroom.
    Two rooms are separated by either walls or transitions./JuPedSim[2017]
    '''
    tag = jps.Room
    
    def __init__(self, osmId, caption='hall'):
        self.attribs = {}
        self.attribs[jps.Id] = osmId
        self.attribs[jps.Caption] = caption
        self.subrooms = []
        self.crossings = []
    
    def addSubroom(self, subroom):
        subroom.attribs[jps.Id] = subroom.attribs[jps.Id]
        self.subrooms.append(subroom)

    def addCrossing(self, crossing):
        self.crossings.append(crossing)
    
class Subroom:
    '''
    Subrooms define the navigation mesh, i.e the walkable areas in the geometry.
    Each subroom is bounded by at least one crossing.JuPedSim[2017]
    Using standard-id 1 for subrooms so far. All rooms consist of a single subroom.
    '''
    tag = jps.Subroom
    
    def __init__(self, subroom_id, jpsClass, caption, jpsC_z):
        self.polygons = []
        self.attribs = {}
        self.attribs[jps.Id] = subroom_id
        self.attribs[jps.Caption] = caption
        self.attribs[jps.Class] = jpsClass
        self.attribs[jps.A_x] = '0'
        self.attribs[jps.B_y] = '0'
        self.attribs[jps.C_z] = jpsC_z
        
    def addPolygon(self, p, room_id, nodeRefs = []):
        if isinstance(p, Polygon) and len(p.vertices) == 2:
            for transition in Geometry.transitions:
                if transition.attribs[jps.Room1]==room_id or transition.attribs[jps.Room2]==room_id:
                    if set(transition.nodeRefs) == set(nodeRefs):
                        return
            for crossing in Geometry.rooms[room_id].crossings:
                if set(crossing.nodeRefs) == set(nodeRefs):
                    return
        self.polygons.append(p)
    
class Polygon:
    '''
    polygon describes the walls as a sequence of vertices. JuPedSim[2017]
    '''
    tag = jps.Polygon
    
    def __init__(self, vertices = []):
        self.attribs = {}
        self.attribs[jps.Caption] = jps.Wall
        self.vertices = vertices
    
class Vertex:
    '''
    osm node. here as a point with x and y. 
    additionally the osm.Id was added as originalId
    '''
    tag = jps.Vertex
    
    def __init__(self, x, y):
        self.attribs = {}
        self.x = str(round(x, 2))
        self.y = str(round(y, 2))        
        self.attribs[jps.PX] = self.x
        self.attribs[jps.PY] = self.y 
        
    def getOriginalId(self):
        return self.attribs[jps.OriginalId]
    
class Transition:
    '''
    transition
    '''
    tag = jps.Transition
    
    def __init__(self, vertex_1, vertex_2, transition_id, caption, type, room1_id, subroom1_id,
                 room2_id, subroom2_id, nodeRefs = []):
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

class Goal:
    '''
    goal
    '''
    tag = jps.Goal

    def __init__(self, vertices = [], tags = {}):
        self.attribs = tags
        self.vertices = vertices
        
