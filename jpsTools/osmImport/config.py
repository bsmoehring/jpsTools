'''
Created on 07.11.2017

@author: bsmoehring
'''

class Config:
    outputPath = 'D:/Wichtiges/TUBerlin/Masterarbeit/Format_Conversions/'
    #inputFile = 'D:/Wichtiges/TUBerlin/Masterarbeit/Data/Alexanderplatz/Alexanderplatz.osm'
    #inputFile = 'D:/Wichtiges/TUBerlin/Masterarbeit/Data/test/Meckesheim.osm'
    inputFile = 'D:/Wichtiges/TUBerlin/Masterarbeit/Data/test/test.osm'
    stanardWidth = 2 #4 meters
    filterTags = {}
    areaTags = {}
    
    def __init__(self):
        
        self.addFilterTag('railway', 'platform')
        #=======================================================================
        # self.filterTags['railway'] = 'station'
        # self.filterTags['public_transport'] = 'station'
        #=======================================================================
        self.addFilterTag('highway', 'steps')
        self.addFilterTag('highway', 'footway')
        
        self.areaTags['area'] = 'yes'
        
    def addFilterTag(self, key, value):
        if key in self.filterTags:
            self.filterTags[key].append(value)
        else:
            self.filterTags[key] = [value]
            
    def addAreaTag(self, key, value):
        if key in self.areaTags:
            self.areaTags[key].append(value)
        else:
            self.areaTags[key] = [value]
        
    def loadConfig(self, configFile):
        '''
        loading required parameters for the network generation from an external source
        '''
        pass
