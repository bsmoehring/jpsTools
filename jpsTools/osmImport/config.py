'''
Created on 07.11.2017

@author: bsmoehring
'''

class Config:
    outputPath = 'D:/Wichtiges/TUBerlin/Masterarbeit/Format_Conversions/'
    #inputFile = 'D:/Wichtiges/TUBerlin/Masterarbeit/Data/Alexanderplatz/Alexanderplatz.osm'
    inputFile = 'D:/Wichtiges/TUBerlin/Masterarbeit/Data/test/Meckesheim.osm'
    stanardWidth = 2 #4 meters
    filterTags = {}
    areaTags = {}
    
    def __init__(self):
        
        self.filterTags['railway'] = ['platform']
        #=======================================================================
        # self.filterTags['railway'] = 'station'
        # self.filterTags['public_transport'] = 'station'
        #=======================================================================
        self.filterTags['highway'] = ['steps', 'footway']
        
        self.areaTags['area'] = 'yes'
        
    def loadConfig(self, configFile):
        '''
        loading required parameters for the network generation from an external source
        '''
        pass
