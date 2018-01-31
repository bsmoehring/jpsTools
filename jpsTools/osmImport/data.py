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

    def __init__(self, config):
        '''
        Constructor
        '''
        self.config = config
        source = open(self.config.path+self.config.file)
        self.tree = ET.parse(source)
        source.close()
        self.config.transform = Transformation(self.tree)
        self.nodes = {}
        self.elementsToHandle = {}

        self.readOSM()

        print(self.tree)
        print(self.nodes)
        print('Input parsed!')

    def readOSM(self):

        for node in self.tree.iter(tag=osm.Node):
            key = node.attrib.get(osm.Id)
            self.nodes[key] = node

        for elem in self.tree.iter():
            convert = False
            transition = False
            area = False
            if elem.tag in [osm.Way, osm.Relation]:
                for tag in elem.iter(tag=osm.Tag):
                    k = tag.attrib[osm.Key]
                    v = tag.attrib[osm.Value]
                    if k in self.config.filterTags and v in self.config.filterTags[k]:
                        convert = True
                    if k in self.config.transitionTags and v in self.config.transitionTags[k]:
                        transition = True
                    if k in self.config.areaTags and v in self.config.areaTags[k]:
                        area = True

            if not convert and not transition and not area:
                continue
            elif area and transition:
                raise Exception
            nodeRefs = []
            for child in elem.iter(tag=osm.NodeRef):
                nodeRefs.append(child.attrib[osm.Ref])
            XYList = self.config.transform.nodeRefs2XY(nodeRefs, self.nodes)
            if area:
                self.translateArea(elem, XYList)
            elif transition:
                self.translateTransition(elem, XYList)
            elif convert:
                self.elementsToHandle[elem.attrib[osm.Id]] = elem


    def translateTransition(self, elem, XYList):
        for child in elem.iter(tag = osm.Tag):
            try:
                if child.attrib[osm.Key] == jps.Room1:
                    osmId1 = child.attrib[osm.Value]
            except KeyError:
                pass
            try:
                if child.attrib[osm.Key] == jps.Room2:
                    osmId2 = child.attrib[osm.Value]
            except KeyError:
                pass

        try: osmId1
        except NameError:
            osmId1 = '-1'
        try: osmId2
        except NameError:
            osmId2 = '-1'

        Output.transitionlst.append(Output.Transition(geometry.LineString(XYList), osmId1, osmId2))

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
    #[Transition]
    transitionlst = []

    class Transition():
        '''

        '''
        def __init__(self, geometry, osmId1, osmId2):
            self.geometry = geometry
            self.osmId1 = osmId1
            self.osmId2 = osmId2
            print('Transition', osmId1, osmId2, geometry)

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
