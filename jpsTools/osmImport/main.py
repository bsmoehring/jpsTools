'''
Created on 24.10.2017

@author: bsmoehring
'''

from config import Config
from coords import Transformation
from handler import ElementHandler
from osmImport.data import Input
from jpsElements import JPSBuilder
from osmElements import OSMBuilder
from plot import ElementPlotter

def main():
    
    Config()
    
    inputData = Input(Config.inputFile)
    
    transform = Transformation(inputData)
    
    handler = ElementHandler(inputData, transform)
    
    handler.readOSM()
    
    OSMBuilder(Config.outputPath, transform)
    
    JPSBuilder(Config.outputPath)
    
    ElementPlotter(transform).plotOutput()

if      __name__ == "__main__":
    main()
