'''
Created on 24.10.2017

@author: bsmoehring
'''
import sys

from config import Config
from coords import Transformation
from handler import ElementHandler
from data import Input
from jpsElements import JPSBuilder
from osmElements import OSMBuilder
from plot import ElementPlotter

def main():

    config = Config(str(sys.argv[1]), str(sys.argv[2]))
    # ADD OR MODIFY YOUR TAGS HERE:
    config.addFilterTag('railway', 'platform')
    config.addFilterTag('highway', 'steps')
    config.addFilterTag('highway', 'footway')
    config.addUnhandleTag('highway', 'elevator')

    Input(config)

    handler = ElementHandler(config)

    try:
        if str(sys.argv[3]) == 'handle':
            handler.runHandler()
    except IndexError: pass
    
    OSMBuilder(config)
    
    JPSBuilder(config.path)
    
    #ElementPlotter(config.transform).plotOutput()

if      __name__ == "__main__":
    main()
