'''
Created on 24.10.2017

@author: bsmoehring
'''
import sys

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
    
    handler = ElementHandler(inputData, transform)

    handler.readOSM()
    
    OSMBuilder(path, transform)
    
    JPSBuilder(path)
    
    ElementPlotter(transform).plotOutput()

if      __name__ == "__main__":
    main()
