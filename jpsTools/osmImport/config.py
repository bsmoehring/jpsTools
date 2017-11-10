'''
Created on 07.11.2017

@author: bsmoehring
'''

class Config:
    outputPath = 'D:/Wichtiges/TUBerlin/Masterarbeit/Format_Conversions/'
    #inputFile = 'D:/Wichtiges/TUBerlin/Masterarbeit/Data/Alexanderplatz/Alexanderplatz.osm'
    inputFile = 'D:/Wichtiges/TUBerlin/Masterarbeit/Data/test/Meckesheim.osm'
    
    tags = {}
    
    def __init__(self):
        
        self.tags['railway'] = 'platform'
        #=======================================================================
        # self.tags['railway'] = 'station'
        # self.tags['public_transport'] = 'station'
        #=======================================================================
        self.tags['highway'] = 'steps'
        self.tags['area'] = 'yes'
        
    def loadConfig(self, configFile):
        '''
        loading required parameters for the network generation from an external source
        '''
        pass
