'''
Created on 21.11.2017

@author: bsmoehring
'''
import logging
from xml.etree import ElementTree as ET
from constants import osm

class Input(object):
    '''
    class to store the input-xml as tree and all nodes of this file separately as nodes
    '''

    def __init__(self, config):
        '''
        Constructor
        '''

        self.tree = ET.parse(config.path+config.file)
        self.nodes = {}
        self.elements = {}

        self.readOSM(config)

        print(self.tree)
        print(self.nodes)
        print('Input parsed!')



    def readOSM(self, config):

        for node in self.tree.iter(tag=osm.Node):
            key = node.attrib.get(osm.Id)
            self.nodes[key] = node

        for elem in self.tree.iter():
            if elem.tag in [osm.Way, osm.Relation]:
                convert = False
                for tag in elem.iter(tag=osm.Tag):
                    k = tag.attrib[osm.Key]
                    v = tag.attrib[osm.Value]
                    if k in config.filterTags and v in config.filterTags[k]:
                        convert = True
                        break
                    if k in config.transitionTags and v in config.transitionTags[k]:
                        pass
                if convert:
                    self.elements[elem.attrib[osm.Id]] = elem

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
