'''
Created on 07.11.2017

@author: bsmoehring
'''
from constants import jps, osm, jpsReport
from data import Output, Input
from io import StringIO
from lxml.etree import SubElement, Element, tostring, parse, XMLParser
import numpy as np

class JPSBuilder(object):
    
    def __init__(self, config):
        self.levelAltsDic = config.levelAltsDic
        self.translate2jps()
        outGeometry = self.buildJPSGEOtree()
        self.tree2xml(outGeometry, config.path+'jps_geo.xml')
        outIni = self.buildJPSINItree()
        self.tree2xml(outIni, config.path+'jps_ini.xml')
        outJPSReportIni = self.buildJPSReportINItree()
        self.tree2xml(outJPSReportIni, config.path+'jps_report_ini.xml')

    def translate2jps(self):
        print('---')
        for way in Output.transitionlst:
            self.transition2jps(way)
        print ('---')
        for room_id, subroomLst in Output.subroomDic.items():
            self.room2jps(room_id, subroomLst)
        print ('---')
        for way in Output.obstacleLst:
            self.obstacle2jps(way)
        #for way in OSMOut.ways:
        #    self.way2jps(way)
        print('---')
        for goal in Output.goalLst:
            self.goal2jps(goal)
        print('---')
        for measurementB in Output.measurementBLst:
            self.measurementB2jps(measurementB)
        print('---')
        for measurementL in Output.measurementLLst:
            self.measurementL2jps(measurementL)
                    
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
            for id, subroom in room.subrooms.items():
                outSubroom = SubElement(outRoom, subroom.tag, subroom.attribs)
                for polygon in subroom.polygons:
                    outPoly = SubElement(outSubroom, polygon.tag, polygon.attribs)
                    for vertex in polygon.vertices:
                        SubElement(outPoly, jps.Vertex, vertex.attribs)
                        #print vertex.attribs
                if subroom.attribs[jps.Class] == jps.Stair or subroom.attribs[jps.Class].startswith(jps.Escalator):
                    SubElement(outSubroom, jps.Down, {jps.PX:subroom.downPX, jps.PY:subroom.downPY, jps.PZ:subroom.downPZ})
                    SubElement(outSubroom, jps.Up, {jps.PX:subroom.upPX, jps.PY:subroom.upPY, jps.PZ:subroom.upPZ})
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
            ax, by, cz, upPX, upPY, upPZ, downPX, downPY, downPZ = self.getPlaneEquation(subroom)
            jpsSubroom = Subroom(subroom.subroom_id, subroom.jpsClass, ax, by, cz, upPX, upPY, upPZ, downPX, downPY, downPZ)
            index = 0
            while index < len(subroom.nodeRefs) - 1:
                jpsVertex1 = Vertex(Input.nodes[subroom.nodeRefs[index]].attrib[jps.PX], Input.nodes[subroom.nodeRefs[index]].attrib[jps.PY])
                jpsVertex2 = Vertex(Input.nodes[subroom.nodeRefs[index + 1]].attrib[jps.PX], Input.nodes[subroom.nodeRefs[index + 1]].attrib[jps.PY])
                jpsWall = Polygon([jpsVertex1, jpsVertex2])
                jpsSubroom.addPolygon(jpsWall, room_id, [subroom.nodeRefs[index], subroom.nodeRefs[index + 1]])
                index += 1

            Geometry().rooms[room_id].addSubroom(jpsSubroom)

    def getPlaneEquation(self, subroom):
        if subroom.jpsClass != jps.Stair and not subroom.jpsClass.startswith(jps.Escalator):
            cz = str(self.levelAltsDic[subroom.level])
            return str(0), str(0), str(cz), None, None, None, None, None, None
        pxDic = {}
        pyDic = {}
        for nodeRef in list(set(subroom.nodeRefs)):
            n = Input.nodes[nodeRef]
            if n.attrib[jps.PZ] in pxDic:
                pxDic[n.attrib[jps.PZ]].append(n.attrib[jps.PX])
            else:
                pxDic[n.attrib[jps.PZ]] =  [n.attrib[jps.PX]]
            if n.attrib[jps.PZ] in pyDic:
                pyDic[n.attrib[jps.PZ]].append(n.attrib[jps.PY])
            else:
                pyDic[n.attrib[jps.PZ]] =  [n.attrib[jps.PY]]
        if len(pxDic) != 2 or len(pyDic) != 2:
            raise Exception
        downZ = min(pxDic, key=pxDic.get)
        upZ = max(pxDic, key=pxDic.get)
        upPX = sum(pxDic[upZ]) / len(pxDic[upZ])
        upPY = sum(pyDic[upZ]) / len(pyDic[upZ])
        downPX = sum(pxDic[downZ]) / len(pxDic[downZ])
        downPY = sum(pyDic[downZ]) / len(pyDic[downZ])

        n = Input.nodes[subroom.nodeRefs[0]]
        p1 = np.array([n.attrib[jps.PX], n.attrib[jps.PY], n.attrib[jps.PZ]])
        n = Input.nodes[subroom.nodeRefs[1]]
        p2 = np.array([n.attrib[jps.PX], n.attrib[jps.PY], n.attrib[jps.PZ]])
        n = Input.nodes[subroom.nodeRefs[2]]
        p3 = np.array([n.attrib[jps.PX], n.attrib[jps.PY], n.attrib[jps.PZ]])

        # These two vectors are in the plane
        v1 = p3 - p1
        v2 = p2 - p1

        # the cross product is a vector normal to the plane
        cp = np.cross(v1, v2)
        ax, by, cz = cp

        # This evaluates a * x3 + b * y3 + c * z3 which equals d
        d = np.dot(cp, p3)

        ax = -ax / cz
        by = -by / cz
        cz = d / cz

        return str(round(ax, 2)), str(round(by, 2)), str(round(cz, 2)), str(round(upPX, 2)), str(round(upPY, 2)), str(round(upZ, 2)), str(round(downPX, 2)), str(round(downPY, 2)), str(round(downZ, 2))

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
        JPScoreIni().addTransition(jpsTransition)

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

        :param goal:
        :return:
        '''
        vertices = []
        for nodeRef in goal.nodeRefs:
            vertices.append(Vertex(Input.nodes[nodeRef].attrib[jps.PX], Input.nodes[nodeRef].attrib[jps.PY]))
        JPScoreIni().addGoal(Goal(vertices, goal.tags))

    def obstacle2jps(self, obstacle):
        '''

        :param obstacle:
        :return:
        '''
        vertices = []
        for nodeRef in obstacle.nodeRefs:
            vertices.append(Vertex(Input.nodes[nodeRef].attrib[jps.PX], Input.nodes[nodeRef].attrib[jps.PY]))

        jpsObstacle = Obstacle(vertices, obstacle.tags)
        Geometry().getRoomById(obstacle.tags[jps.Room_ID]).getSubroomById(obstacle.tags[jps.Subroom_ID]).addObstacle(jpsObstacle)

    def measurementB2jps(self, measurementB):
        '''

        :param measurementB:
        :return:
        '''
        vertices = []
        for nodeRef in measurementB.nodeRefs:
            vertices.append(Vertex(Input.nodes[nodeRef].attrib[jps.PX], Input.nodes[nodeRef].attrib[jps.PY]))
        zPos = str(self.levelAltsDic[measurementB.level])
        JPSreportIni().addAreaB(AreaB(measurementB.measurement_id, zPos, vertices))

    def measurementL2jps(self, measurementL):
        '''

        :param measurementL:
        :return:
        '''
        vertices = []
        for nodeRef in measurementL.nodeRefs:
            vertices.append(Vertex(Input.nodes[nodeRef].attrib[jps.PX], Input.nodes[nodeRef].attrib[jps.PY]))
        zPos = str(self.levelAltsDic[measurementL.level])
        JPSreportIni().addAreaL(AreaL(measurementL.measurement_id, zPos, vertices))

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

        parser = XMLParser(remove_blank_text=True)
        outIni = parse('resources/example_ini.xml', parser).getroot()

        #outIni = Element(IniFile().tag, attribs)
        outRouting = SubElement(outIni, 'routing')
        outGoals = SubElement(outRouting, 'goals')
        for goal in JPScoreIni().goals:
            outGoal = SubElement(outGoals, 'goal', goal.attribs)
            outPolygon = SubElement(outGoal, jps.Polygon)
            for vertex in goal.vertices:
                SubElement(outPolygon, jps.Vertex, vertex.attribs)
                # print vertex.attribs
        outTrafficConstraints = SubElement(outIni, 'traffic_constraints')
        outDoors = SubElement(outTrafficConstraints, 'doors')
        for transition in JPScoreIni().transitions:
            attribs = {}
            attribs['trans_id']=transition.attribs[jps.Id]
            attribs[jps.Caption]=transition.attribs[jps.Caption]
            attribs['state']='open'
            SubElement(outDoors, 'door', attribs)

        outAgents = SubElement(outIni, 'agents', {'operational_model_id':'3'})
        outAgentsDistribution = SubElement(outAgents, 'agents_distribution')
        
        group_id = 1
        for goalFrom in JPScoreIni().goals:
            for goalTo in JPScoreIni().goals:
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

    def buildJPSReportINItree(self):
        '''
        form an xml string from all jpsreport objects
        '''
        print('---')

        parser = XMLParser(remove_blank_text=True)
        outJPSReportIni = parse('resources/example_jpsreport_ini.xml', parser).getroot()

        outMeasurementAreas = SubElement(outJPSReportIni, 'measurement_areas', {'unit':'m'})
        for measurementB in JPSreportIni.measurementAreasB:
            measurementAreaB = SubElement(outMeasurementAreas, measurementB.tag, measurementB.attribs)
            for vertex in measurementB.vertices:
                SubElement(measurementAreaB, jps.Vertex, vertex.attribsJPSReport)
            SubElement(measurementAreaB, jpsReport.length_in_movement_direction, {jpsReport.Distance:'1.0'})
        for measurementL in JPSreportIni.measurementAreasL:
            measurementAreaL = SubElement(outMeasurementAreas, measurementL.tag, measurementL.attribs)
            vertex = measurementL.vertices[0]
            SubElement(measurementAreaL, jpsReport.Start, vertex.attribsJPSReport)
            vertex = measurementL.vertices[1]
            SubElement(measurementAreaL, jpsReport.End, vertex.attribsJPSReport)
        return outJPSReportIni


class JPScoreIni:
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

class JPSreportIni:
    tag = 'JPSreport'
    measurementAreasB = []
    measurementAreasL = []
    methodAList = []
    methodBList = []
    methodCList = []
    methodDList = []

    def addAreaB(self, areaB):
        '''

        :param areaB:
        :return:
        '''
        self.measurementAreasB.append(areaB)

    def addAreaL(self, areaL):
        '''

        :param areaL:
        :return:
        '''

        self.measurementAreasL.append(areaL)

class AreaB:
    tag = jpsReport.AreaB

    def __init__(self, area_id, zPos, vertices):
        self.attribs = {}
        self.attribs[jpsReport.Id] = area_id
        self.attribs[jpsReport.Type] = jpsReport.BoundingBox
        self.attribs[jpsReport.ZPos] = zPos
        self.vertices = []
        self.vertices.append(vertices[0])
        self.vertices.append(vertices[1])
        self.vertices.append(vertices[2])
        self.vertices.append(vertices[3])

class AreaL:
    tag = jpsReport.AreaL

    def __init__(self, area_id, zPos, vertices):
        self.attribs = {}
        self.attribs[jpsReport.Id] = area_id
        self.attribs[jpsReport.Type] = jpsReport.Line
        self.attribs[jpsReport.ZPos] = zPos
        self.vertices = []
        self.vertices.append(vertices[0])
        self.vertices.append(vertices[1])

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

    def getRoomById(self, room_id):
        return self.rooms[room_id]

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
        self.subrooms = {}
        self.crossings = []
    
    def addSubroom(self, subroom):
        self.subrooms[subroom.attribs[jps.Id]] = subroom

    def getSubroomById(self, subroom_id):
        return self.subrooms[subroom_id]

    def addCrossing(self, crossing):
        self.crossings.append(crossing)
    
class Subroom:
    '''
    Subrooms define the navigation mesh, i.e the walkable areas in the geometry.
    Each subroom is bounded by at least one crossing.JuPedSim[2017]
    Using standard-id 1 for subrooms so far. All rooms consist of a single subroom.
    '''
    tag = jps.Subroom
    
    def __init__(self, subroom_id, jpsClass, ax, by, cz, upPX, upPY, upPZ, downPX, downPY, downPZ):
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

    def addObstacle(self, obstacle):
        self.obstacles.append(obstacle)
    
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
        self.attribsJPSReport = {}
        self.attribsJPSReport[jpsReport.X] = self.x
        self.attribsJPSReport[jpsReport.Y] = self.y

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

class Obstacle:
    '''
    obstacle
    '''
    tag = jps.Obstacle

    def __init__(self, vertices = [], tags ={}):
        self.attribs = tags
        self.vertices = vertices
        
