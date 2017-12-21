'''
Created on 07.11.2017

@author: bsmoehring
'''

class Config:
    outputPath = 'D:/Wichtiges/TUBerlin/Masterarbeit/Format_Conversions/'
    #inputFile = 'D:/Wichtiges/TUBerlin/Masterarbeit/Data/Alexanderplatz/Alexanderplatz.osm'
    #inputFile = 'D:/Wichtiges/TUBerlin/Masterarbeit/Data/test/Meckesheim.osm'
    inputFile = 'D:/Wichtiges/TUBerlin/Masterarbeit/Data/test/test.osm'
    # inputFile = 'D:/Wichtiges/TUBerlin/Masterarbeit/Data/test/test1.osm'
    
    stanardWidth = 2 #meters
    #points are merged if their distance is below errorDistance
    errorDistance = 0.001
    
    filterTags = {}
    areaTags = {}
    unhandleTag = {}
    
    def __init__(self):
        
        self.addFilterTag('railway', 'platform')
        #=======================================================================
        # self.filterTags['railway'] = 'station'
        # self.filterTags['public_transport'] = 'station'
        #=======================================================================
        self.addFilterTag('highway', 'steps')
        self.addFilterTag('highway', 'footway')
        
        self.addUnhandleTag('highway', 'elevator')
        
        self.addAreaTag('area', 'yes')
        
    def addFilterTag(self, key, value):
        if key in self.filterTags:
            self.filterTags[key].append(value)
        else:
            self.filterTags[key] = [value]
    
    def addUnhandleTag(self, key, value):
        if key in self.unhandleTag:
            self.unhandleTag[key].append(value)
        else:
            self.unhandleTag[key] = [value]
            
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
