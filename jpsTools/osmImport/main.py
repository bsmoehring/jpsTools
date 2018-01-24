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

    path = str(sys.argv[1])
    file = str(sys.argv[2])
    if not path.endswith('/'):
        path += '/'

    inputData = Input(path + file)

    transform = Transformation(inputData)

    config = Config(transform)
    
    handler = ElementHandler(inputData, config)

    handler.readOSM()
    
    OSMBuilder(path, config)
    
    JPSBuilder(path)
    
    ElementPlotter(transform).plotOutput()

if      __name__ == "__main__":
    main()
