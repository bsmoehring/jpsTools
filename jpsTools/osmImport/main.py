'''
Created on 24.10.2017

@author: bsmoehring
'''

from lxml.etree import tostring 
from constants import osm
from jpsElements import translate2jps, buildJPSTree
from config import Config
from coords import Transformation
from handler import ElementHandler
import logging
from osmImport.data import Input
from plot import plot

def main():
    
    logging.basicConfig(filename=Config().outputPath+'tes.log',level=logging.DEBUG)
    
    logging.info('Start')
    
    input = Input(Config.inputFile)
    
    transform = Transformation(input.tree.find(osm.Bounds))
    
    handler = ElementHandler(input, transform)
    
    readOSM(input, handler)
    
    #plot(transform)
    
    translate2jps()
                  
    outgeometry = buildJPSTree()
    
    tree2xml(outgeometry)
    
    logging.info('operation finished!')


def readOSM(input, handler):
    
    elements = {}
    for elem in input.tree.iter():
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
            handler.handle(elem)  

def tree2xml(outGeometry):
    '''
    writes the ElementTree geometry to a xml file
    '''
    out = tostring(outGeometry, pretty_print=True)
    print '---'
    #print out
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
