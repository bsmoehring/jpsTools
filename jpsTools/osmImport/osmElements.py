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
from osmImport import constants

class OSMBuilder(object):
    
    def __init__(self, outputPath, transform):
        self.transform = transform
        self.translate2osm()
        self.buildOSMTree()
        self.tree2xml(outputPath)
        
    def translate2osm(self):
        print '---'
        for osmId, poly in Output.polygons.items():
            print osmId
            elem = Output.elements[osmId]
            if isinstance(poly, geometry.Polygon):
                self.polygon2osm(osmId, poly, elem)
        transitionId = 1
        for transition in Output.transitionlst:
            nodeRefs = []
            nodeRefPrevious = ''
            if isinstance(transition.geometry, geometry.Polygon):
                for coord in transition.geometry.exterior._get_coords():
                    lat, lon = self.transform.XY2WGS(coord[0], coord[1])
                    nodeRef = OSM().getOrAddNode(coord[0], coord[1], lat, lon, {})
                    if nodeRef != nodeRefPrevious:
                        nodeRefs.append(nodeRef)
                    nodeRefPrevious = nodeRef
            elif isinstance(transition.geometry, geometry.LineString):
                for coord in transition.geometry.coords:
                    lat, lon = self.transform.XY2WGS(coord[0], coord[1])
                    nodeRef = OSM().getOrAddNode(coord[0], coord[1], lat, lon, {})
                    if nodeRef != nodeRefPrevious:
                        nodeRefs.append(nodeRef)
                    nodeRefPrevious = nodeRef
            if len(nodeRefs)==3:
                del nodeRefs[-1]
            if len(nodeRefs)==2:
                tags = {'origin':'JPSTools', 'highway':'transition', 'osmId1':transition.osmId1, 'osmId2':transition.osmId2}
                OSM().addWay(Way(transitionId, nodeRefs, tags))
                print transitionId
                transitionId += 1
            
    def polygon2osm(self, osmId, poly, elem = None):
        
        nodeRefs = []
        tags = {}
        nodeRefPrevious = ''
        for coord in poly.exterior._get_coords():
            lat, lon = self.transform.XY2WGS(coord[0], coord[1])
            nodeRef = OSM().getOrAddNode(coord[0], coord[1], lat, lon, {})
            if nodeRef != nodeRefPrevious:
                nodeRefs.append(nodeRef)
            nodeRefPrevious = nodeRef
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
            for k, v in way.tags.iteritems():
                SubElement(outWay, osm.Tag, {osm.Key:k, osm.Value:v})   
            
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
        returning a node reference either from an existing node or from a newly created node
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
        self.tags = tags
    
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
        
        
        