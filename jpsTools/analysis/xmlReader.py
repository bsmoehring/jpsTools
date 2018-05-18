import xml.etree.cElementTree as ET

class Reader():
    '''

    '''


    def __init__(self, inputfile, xmin, xmax, ymin, ymax, z):

        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.z = z

        self.inputfile = inputfile

    def read(self):

        pass