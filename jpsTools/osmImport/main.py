'''
Created on 24.10.2017

@author: bsmoehring
'''

from config import Config
from coords import Transformation
from handler import ElementHandler
import logging
from osmImport.data import Input
from jpsElements import JPSBuilder
from osmElements import OSMBuilder
from plot import ElementPlotter

def main():
    
    logging.basicConfig(filename=Config().outputPath+'tes.log',level=logging.DEBUG)
    
    logging.info('Start')
    
    input = Input(Config.inputFile)
    
    transform = Transformation(input)
    
    handler = ElementHandler(input, transform)
    
    handler.readOSM()
    
    #handler.getTransitions()
    
    JPSBuilder(Config.outputPath)
    
    OSMBuilder(Config.outputPath, transform)
    
    logging.info('operation finished!')
    
    ElementPlotter(transform).plotOutput()


if      __name__ == "__main__":
    main()
