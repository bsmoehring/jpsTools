'''
Created on 24.10.2017

@author: bsmoehring
'''

from xml.etree import ElementTree as ET
from lxml.etree import tostring 
from constants import osm
from jpsElements import translate2jps, buildJPSTree
from config import Config
from coords import Transformation
from handler import ElementHandler
import logging

def main():
    
    logging.info('Start')
    
    transform = Transformation(Input.tree.find(osm.Bounds))
    
    handler = ElementHandler(Input.tree, Input.allNodes)
    
    readOSM(handler, transform)
    
    translate2jps()
                  
    outgeometry = buildJPSTree()
    
    tree2xml(outgeometry)
    
    logging.info('operation finished!')

class Input:
    '''
    class to store the input-xml as tree and all nodes of this file separately as nodes
    '''
    logging.basicConfig(filename=Config().outputPath+'tes.log',level=logging.DEBUG)
    tree = ET.parse(Config().inputFile)
    allNodes = {}
    
    for node in tree.iter(tag=osm.Node):
        key = node.attrib.get(osm.Id)
        allNodes[key] = node 
    logging.info('Input loaded.') 

def readOSM(handler, transform):
    
    elements = {}
    for elem in Input.tree.iter():
        if elem.tag in [osm.Way, osm.Relation]:
            count = 0
            convert = False
            for tag in elem:
                k = tag.get(osm.Key)
                v = tag.get(osm.Value)
                if k in Config.filterTags and v in Config.filterTags[k]:
                    convert = True
            if convert:
                try: 
                    elements[count].append(elem)
                except KeyError:
                    elements[count] = [elem]
    
    #sort list to start with largest elements
    for count in sorted(elements.iterkeys(), reverse=True): 
        for elem in elements[count]:
            handler.handle(elem, transform)  

def tree2xml(outGeometry):
    '''
    writes the ElementTree geometry to a xml file
    '''
    out = tostring(outGeometry, pretty_print=True)
    print '---'
    print out
    if Config.outputPath.endswith('.xml'):
        pass
    else:
        Config.outputPath += 'test.xml' 
    try:
        f = open(Config.outputPath, 'w')
        f.write(out)
        f.close()
    except Exception:
        print 'output not written!'
    
if      __name__ == "__main__":
    main()
