'''
Created on Dec 13, 2017

@author: user
'''

from config import Config
from constants import osm
from data import Output
from shapely import geometry
from lxml.etree import SubElement, Element
from lxml.etree import tostring 

class OSMBuilder(object):
    
    def __init__(self, outputPath, transform):
        self.transform = transform
        self.translate2osm()
        self.buildOSMTree()
        self.tree2xml(outputPath)
        
    def translate2osm(self):
        print '---'
        for osmId, poly in Output.polygons.items():
            try:
                elem = Output.elements[osmId]
            except KeyError:
                elem = None
            if isinstance(poly, geometry.Polygon):
                self.polygon2osm(osmId, poly, elem)
            elif isinstance(poly, geometry.MultiPolygon):
                for polygon in poly:
                    self.polygon2osm(osmId, polygon, elem)
            else: 
                print poly
                raise Exception
        #TODO transitions2osm
            
    def polygon2osm(self, osmId, poly, elem = None):
        
        nodeRefs = []
        tags = {}
        for coord in poly.exterior._get_coords():
            lat, lon = self.transform.XY2WGS(coord[0], coord[1])
            nodeRef = OSM().getOrAddNode(coord[0], coord[1], lat, lon, {})
            nodeRefs.append(nodeRef)
        
        if elem == None:
            tags = {osm.Id:osmId, 'origin':'JPSTools', 'highway':'footway', 'area':'yes'}
        else:
            for tag in elem.iter(tag = osm.Tag):
                k = tag.attrib[osm.Key] 
                v = tag.attrib[osm.Value]
                tags[k] = v
            
        OSM().addWay(Way(osmId, nodeRefs, tags))
        
    def buildOSMTree(self):
        '''
        form an xml string from all objects
        '''
        print '---'
        
        #required attributes of the geometry element
        attribs = {}
        attribs['version'] = '0.6' 
        attribs['generator'] = 'JPSTools'
          
        osmTree = Element(OSM.tag, attribs)
        for node in OSM.nodes:
            outNode = SubElement(osmTree, node.tag, node.attribs)
            for tag in node.tags.iteritems():
                SubElement(outNode, tag.tag, tag.attribs)
        
        for way in OSM.ways:
            outWay = SubElement(osmTree, way.tag, way.attribs)
            for nodeRef in way.nodeRefs:
                SubElement(outWay, osm.NodeRef, {osm.Ref: str(nodeRef)})
            for tag in way.tags.iteritems():
                SubElement(outWay, tag.tag, tag.attribs)   
            
        self.osmTree = osmTree
    
    def tree2xml(self, outputPath):
        '''
        writes the ElementTree geometry to a xml file
        '''
        out = tostring(self.osmTree, pretty_print=True)
        print '---'
        #print out
        if outputPath.endswith('.osm'):
            pass
        else:
            outputPath += 'testOSMout.osm' 
        try:
            f = open(outputPath, 'w')
            f.write(out)
            f.close()
            print 'output written to', outputPath
        except Exception:
            print 'output not written!'
            
class OSM:
    tag = osm.Osm
    nodes = []
    ways = []
    relations = []
        
    def getOrAddNode(self, x, y, lat, lon, tags = {}):
        '''
        
        '''
        #checking all exisitng nodes if one is the same and can be used
        pNew = geometry.Point(x, y)
        for node in self.nodes:
            pOld = geometry.Point(node.x, node.y)
            if pNew.distance(pOld) < Config.errorDistance:
                return node.attribs[osm.Id]
        
        #creating new node
        nodeRef = -(len(self.nodes)+1)
        node = Node(nodeRef, x, y, lat, lon, tags)
        self.nodes.append(node)
        return nodeRef
    
    def addWay(self, way):
        '''
        '''
        self.ways.append(way)
        
    def addRelation(self, relation):
        pass
    
class Node:
    '''
    OSM node
    '''
    tag = osm.Node
    
    def __init__(self, id, x, y, lat, lon, tags = {}):
        self.x = x
        self.y = y
        self.attribs = {}
        self.attribs[osm.Id] = str(id)
        self.attribs[osm.Lat] = str(lat)
        self.attribs[osm.Lon] = str(lon)
        self.tags = tags
    
class Way:
    '''
    OSM way
    '''
    tag = osm.Way
    
    def __init__(self, id, nodeRefs = [], tags = {}):
        self.attribs = {}
        self.attribs[osm.Id] = str(id)
        self.attribs['version'] = '9999999'
        self.nodeRefs = nodeRefs
        self.tags = {}
    
class Relation:
    '''
    OSM relation
    '''
    tag = osm.Relation

class Tag:
    '''
    OSm tag
    '''
    tag = osm.Tag
    
    def __init__(self, key, value):
        self.attribs = {}
        self.attribs[osm.Key] = key
        self.attribs[osm.Value] = value
        
        
        