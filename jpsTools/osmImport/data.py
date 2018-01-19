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

    def __init__(self, inputFile):
        '''
        Constructor
        '''

        self.tree = ET.parse(inputFile)
        self.allNodes = {}

        for node in self.tree.iter(tag=osm.Node):
            key = node.attrib.get(osm.Id)
            self.allNodes[key] = node
        logging.info('Input loaded.')

        print(self.tree)
        print(self.allNodes)

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
