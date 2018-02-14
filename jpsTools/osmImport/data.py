'''
Created on 21.11.2017

@author: bsmoehring
'''
import logging
from xml.etree import ElementTree as ET
from constants import osm, jps
from coords import Transformation
from shapely import geometry

class Input(object):
    '''
    class to store the input-xml as tree and all nodes of this file separately as nodes
    '''
    elementsToHandle = {}
    nodes = {}

    def __init__(self, config, handle):
        '''
        Constructor
        '''
        self.config = config
        source = open(self.config.path+self.config.file)
        self.tree = ET.parse(source)
        source.close()
        self.config.transform = Transformation(self.tree)

        self.readOSM(handle)

        print(self.tree)
        print(self.nodes)
        print('Input parsed!')

    def readOSM(self, handle = False):

        for node in self.tree.iter(tag=osm.Node):
            key = node.attrib.get(osm.Id)
            self.nodes[key] = node

        for elem in self.tree.iter(tag=osm.Way):
            subroom = False
            transition = False
            crossing = False
            goal = False
            convert = False
            area = False
            if elem.tag in [osm.Way, osm.Relation]:
                try:
                    if elem.attrib['action']=='delete':
                        continue
                except KeyError:
                    pass
                for tag in elem.iter(tag=osm.Tag):
                    k = tag.attrib[osm.Key]
                    v = tag.attrib[osm.Value]
                    if k == jps.JuPedSim and v == jps.Subroom:
                        subroom = True
                    if k == jps.JuPedSim and v == jps.Crossing:
                        crossing = True
                    if k == jps.JuPedSim and v == jps.Transition:
                        transition = True
                    if k == jps.JuPedSim and v == jps.Goal:
                        goal = True
                    if k in self.config.filterTags and v in self.config.filterTags[k]:
                        convert = True
                    if k in self.config.filterTags and v in self.config.filterTags[k]:
                        convert = True
                    if k in self.config.areaTags and v == self.config.areaTags[k]:
                        area = True

            nodeRefs = []
            for child in elem.iter(tag=osm.NodeRef):
                nodeRefs.append(child.attrib[osm.Ref])
            XYList = self.config.transform.nodeRefs2XY(nodeRefs, self.nodes)

            if subroom:
                self.translateSubroom(elem, XYList)
            elif crossing:
                self.translateCrossing(elem, XYList)
            elif transition:
                self.translateTransition(elem, XYList)
            elif goal:
                self.translateGoal(elem, XYList)
            if not handle:
                continue
            elif area:
                self.translateArea(elem, XYList)
            elif convert:
                self.elementsToHandle[elem.attrib[osm.Id]] = elem

    def translateSubroom(self, elem, XYList):
        for child in elem.iter(tag=osm.Tag):
            try:
                if child.attrib[osm.Key] == jps.Room:
                    room_id = child.attrib[osm.Value]
            except KeyError:
                pass
            try:
                if child.attrib[osm.Key] == jps.Subroom:
                    subroom_id = child.attrib[osm.Value]
            except KeyError:
                pass
        try: subroom_id
        except NameError: subroom_id='0'
        if len(XYList) > 2 and XYList[0] == XYList[-1]:
            poly = geometry.Polygon(XYList)
            subroom = Output.Subroom(geometry=poly, subroom_id=subroom_id)
            if room_id in Output.subroomDic:
                Output.subroomDic[room_id].append(subroom)
            else:
                Output.subroomDic[room_id] = [subroom]
        else:
            raise Exception

    def translateCrossing(self, elem, XYList):
        for child in elem.iter(tag = osm.Tag):
            try:
                if child.attrib[osm.Key] == jps.Room:
                    room_id = child.attrib[osm.Value]
            except KeyError:
                pass
            try:
                if child.attrib[osm.Key] == jps.Subroom1:
                    subroom1_id = child.attrib[osm.Value]
            except KeyError:
                pass
            try:
                if child.attrib[osm.Key] == jps.Subroom2:
                    subroom2_id = child.attrib[osm.Value]
            except KeyError:
                pass
        crossing = Output.Crossing(geometry.LineString(XYList), room_id, subroom1_id, subroom2_id)
        if room_id in Output.crossingDic:
            Output.crossingDic[room_id].append(crossing)
        else: Output.crossingDic[room_id] = [crossing]

    def translateTransition(self, elem, XYList):
        for child in elem.iter(tag = osm.Tag):
            try:
                if child.attrib[osm.Key] == jps.Room1:
                    room1_id = child.attrib[osm.Value]
            except KeyError:
                pass
            try:
                if child.attrib[osm.Key] == jps.Room2:
                    room2_id = child.attrib[osm.Value]
            except KeyError:
                pass
            try:
                if child.attrib[osm.Key] == jps.Subroom1:
                    subroom1_id = child.attrib[osm.Value]
            except KeyError:
                pass
            try:
                if child.attrib[osm.Key] == jps.Subroom2:
                    subroom2_id = child.attrib[osm.Value]
            except KeyError:
                pass

        try: room1_id
        except NameError:
            room1_id = '-1'
        try: room2_id
        except NameError:
            room2_id = '-1'
        try:
            subroom1_id
        except NameError:
            subroom1_id = '0'
        try:
            subroom2_id
        except NameError:
            subroom2_id = '0'

        Output.transitionlst.append(Output.Transition(geometry.LineString(XYList),
                                                      room1_id, room2_id, subroom1_id, subroom2_id))

    def translateGoal(self, elem, XYList):
        if len(XYList) > 2 and XYList[0] == XYList[-1]:
            poly = geometry.Polygon(XYList)
            tags = {}
            for tag in elem.iter(tag=osm.Tag):
                tags[tag.attrib[osm.Key]] = tag.attrib[osm.Value]
            Output.goalLst.append(Output.Goal(geometry.Polygon(XYList), tags))
        else:
            raise Exception

    def translateArea(self, elem, XYList):

        if len(XYList) > 2 and XYList[0] == XYList[-1]:
            poly = geometry.Polygon(XYList)
            Output().storeElement(elem.attrib[osm.Id], elem, poly)
        else:
            raise Exception

class Output(object):
    '''
    class to store output data
    '''
    #osmId Node = [osmId Way]
    usedNodes = {}
    #osmId Way = polygon
    polygons = {}
    #osmId Way = Way/Element
    elements = {}
    #osmId Way = [osmId Node]
    wayNodes = {}


    #room_id = [Subroom]
    subroomDic = {}
    #roomId = [Crossing]
    crossingDic = {}
    #[Transition]
    transitionlst = []
    #[goal]
    goalLst = []

    class Subroom():
        '''

        '''
        def __init__(self, geometry, subroom_id):
            self.geometry = geometry
            self.subroom_id = subroom_id
            print('Subroom', subroom_id, geometry)

    class Transition():
        '''

        '''
        def __init__(self, geometry, room1_id, room2_id, subroom1_id, subroom2_id):
            self.geometry = geometry
            self.room1_id = room1_id
            self.room2_id = room2_id
            self.subroom1_id = subroom1_id
            self.subroom2_id = subroom2_id
            print('Transition', room1_id, room2_id, geometry)

    class Crossing():
        '''

        '''
        def __init__(self, geometry, room_id, subroom1_id, subroom2_id):
            self.geometry = geometry
            self.room_id = room_id
            try: self.crossing_id = str(len(Output.crossingDic[room_id]))
            except KeyError: self.crossing_id = '0'
            self.subroom1_id = subroom1_id
            self.subroom2_id = subroom2_id
            print('Crossing', room_id, subroom1_id, subroom2_id, geometry)

    class Goal():
        '''

        '''
        def __init__(self, geometry, tags):
            self.geometry = geometry
            self.tags = tags

    def storeElement(self, osmId, elem, poly):
        '''
        storing references of the approved polygon in usedNodes{}, polygons{}, elements{} and wayNodes{}
        use the List nodeRefs instead of the elements tags if it's given
        '''
        nodeRefs = []
        for nd in elem.iter(tag=osm.NodeRef):
            nodeRefs.append(nd.attrib[osm.Ref])
        # add nodes and elemId to usedNodes
        for nodeRef in nodeRefs:
            if nodeRef in self.usedNodes:
                # make sure that every node is added only once
                if osmId not in self.usedNodes[nodeRef]:
                    self.usedNodes[nodeRef].append(osmId)
            else:
                self.usedNodes[nodeRef] = [osmId]
        self.wayNodes[osmId] = nodeRefs
        self.polygons[osmId] = poly
        self.elements[osmId] = elem
