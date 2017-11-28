'''
Created on 24.10.2017

@author: bsmoehring
'''

from constants import osm
from config import Config
from coords import Transformation
from handler import ElementHandler
import logging
from osmImport.data import Input, Output
from jpsElements import JPSBuilder
from plot import ElementPlotter

def main():
    
    logging.basicConfig(filename=Config().outputPath+'tes.log',level=logging.DEBUG)
    
    logging.info('Start')
    
    input = Input(Config.inputFile)
    
    transform = Transformation(input.tree.find(osm.Bounds))
    
    handler = ElementHandler(input, transform)
    
    readOSM(input, handler)
    
    JPSBuilder(Config.outputPath)
    
    logging.info('operation finished!')
    
    ElementPlotter(transform).plot()


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
    print 'Rooms', Output.elements

if      __name__ == "__main__":
    main()
