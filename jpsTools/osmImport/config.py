'''
Created on 07.11.2017

@author: bsmoehring
'''

class Config:

    stanardWidth = 2 #meters
    #points are merged if their distance is below errorDistance
    errorDistance = 0.05
    bufferDistance = errorDistance / 50

    filterTags = {}
    areaTags = {}
    unhandleTag = {}
    defaultMandatoryTags = {}
    jpsGoalTags = {}
    jpsTransitionTags = {}

    def __init__(self, path, file, levelAltsDic = {}):

        if not path.endswith('/'):
            path += '/'

        self.path = path

        self.file = file

        self.transform = None

        self.addAreaTag('area', 'yes')

        self.addDefaultMandatoryTag('level', '0')

        self.addGoalTag('jupedsim', 'goal')

        self.addTransitionTag('jupedsim', 'transition')

        self.levelAltsDic = levelAltsDic

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
        self.areaTags[key] = value

    def addDefaultMandatoryTag(self, key, value):
        self.defaultMandatoryTags[key] = value

    def addTransitionTag(self, key, value):
        self.jpsTransitionTags[key] = value

    def addGoalTag(self, key, value):
        self.jpsGoalTags[key] = value


