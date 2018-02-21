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

    levelAltsDic = {}
    levelAltsDic['1'] = 4.2
    levelAltsDic['0'] = 0.0
    levelAltsDic['-1'] = -2.6
    levelAltsDic['-2'] = -3.8
    levelAltsDic['-3'] = -5.7
    levelAltsDic['-4'] = -8.2
    levelAltsDic['-5'] = -11.0

    try:
        if str(sys.argv[3]) == 'handle':
            handle=True
    except IndexError:
        handle = False
    config = Config(str(sys.argv[1]), str(sys.argv[2]), levelAltsDic)
    # ADD OR MODIFY YOUR TAGS HERE:
    config.addFilterTag('railway', 'platform')
    config.addFilterTag('highway', 'steps')
    config.addFilterTag('highway', 'footway')
    config.addUnhandleTag('highway', 'elevator')

    Input(config, handle)

    if handle:
        ElementHandler(config, handle).runHandler()

    
    #OSMBuilder(config)
    
    JPSBuilder(config.path)
    
    #ElementPlotter(config.transform).plotOutput()

if      __name__ == "__main__":
    main()
