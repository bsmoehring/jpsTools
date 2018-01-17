'''
Created on 07.11.2017

@author: bsmoehring
'''

class Config:
    
    inputFile = 'ressources/Meckesheim.osm'
    outputPath = 'ressources'
    
    #outputPath = 'D:/Wichtiges/TUBerlin/Masterarbeit/Format_Conversions/'
    #inputFile = 'D:/Wichtiges/TUBerlin/Masterarbeit/Data/Alexanderplatz/Alexanderplatz.osm'
    #inputFile = 'D:/Wichtiges/TUBerlin/Masterarbeit/Data/test/Meckesheim.osm'
    #inputFile = 'D:/Wichtiges/TUBerlin/Masterarbeit/Data/test/koeln.osm'
    #inputFile = 'D:/Wichtiges/TUBerlin/Masterarbeit/Data/test/test.osm'
    #inputFile = 'D:/Wichtiges/TUBerlin/Masterarbeit/Data/test/test1.osm'
    #inputFile = 'D:/Wichtiges/TUBerlin/Masterarbeit/Format_Conversions/testOSMout.osm'
    
    stanardWidth = 2 #meters
    #points are merged if their distance is below errorDistance
    errorDistance = 0.01
    bufferDistance = errorDistance / 10
    
    filterTags = {}
    areaTags = {}
    unhandleTag = {}
    defaultMandatoryTags = {}
    transitionTags = {}
    
    def __init__(self):
        
        self.addFilterTag('railway', 'platform')
        self.addFilterTag('highway', 'steps')
        self.addFilterTag('highway', 'footway')
        
        #self.addUnhandleTag('highway', 'elevator')
        
        self.addAreaTag('area', 'yes')
        
        self.addDefaultMandatoryTag('level', '0')
        
        self.addTransitionTag('highway', 'transition')
        
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
    
    def addDefaultMandatoryTag(self, key, value):
        self.defaultMandatoryTags[key] = value
        
    def addMandatoryTags(self, tags = {}):
        for key, value in self.defaultMandatoryTags.iteritems():
            try: 
                tags[key]
            except KeyError:
                tags[key] = value
    
    def addTransitionTag(self, key, value):
        if key in self.transitionTags:
            self.transitionTags[key].append(value)
        else:
            self.transitionTags[key] = [value]
        if key in self.filterTags:
            self.filterTags[key].append(value)
        else:
            self.filterTags[key] = [value]
        
    def loadConfig(self, configFile):
        '''
        loading required parameters for the network generation from an external source
        '''
        pass
