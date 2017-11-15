'''
Created on 15.11.2017

@author: bsmoehring
'''
import logging
from config import Config
import xml.etree.ElementTree as ET
from constants import osm

class Input:
    '''
    class to store the input-xml as tree and all nodes of this file separately as nodes
    '''
    logging.basicConfig(filename=Config.outputPath+'tes.log',level=logging.DEBUG)
    print Config.inputFile
    tree = ET 
    bounds = ET
    nodes = {}
    logging.info('Input loaded.') 
    
    def __init__(self):
        self.tree = ET.parse(Config.inputFile)
        self.bounds = self.tree.find(osm.Bounds)
        for node in self.tree.iter(tag=osm.Node):
            key = node.attrib.get(osm.Id)
            self.nodes[key] = node
    