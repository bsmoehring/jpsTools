'''
Created on 07.11.2017

@author: bsmoehring
'''

class Config:

    stanardWidth = 2 #meters
    #points are merged if their distance is below errorDistance
    errorDistance = 0.01
    bufferDistance = errorDistance / 10

    filterTags = {}
    areaTags = {}
    unhandleTag = {}
    defaultMandatoryTags = {}
    transitionTags = {}

    def __init__(self, path, file):

        if not path.endswith('/'):
            path += '/'

        self.path = path

        self.file = file

        self.transform = None

        self.addAreaTag('area', 'yes')

        self.addDefaultMandatoryTag('level', '0')

        self.addTransitionTag('jupedsim', 'transition')

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
        if key in self.transitionTags:
            self.transitionTags[key].append(value)
        else:
            self.transitionTags[key] = [value]

