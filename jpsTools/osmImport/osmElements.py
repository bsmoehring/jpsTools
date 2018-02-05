'''
Created on Dec 13, 2017

@author: bsmoehring
'''

from constants import osm, jps
from data import Output
from shapely import geometry
from lxml.etree import SubElement, Element
from lxml.etree import tostring 

class OSMBuilder(object):
    
    def __init__(self, config):
        self.config = config
        self.translate2osm()
        self.buildOSMTree()
        self.tree2xml(config.path)
        
    def translate2osm(self):
        print ('---')
        for osmId, poly in Output.polygons.items():
            print (osmId)
            elem = Output.elements[osmId]
            if isinstance(poly, geometry.Polygon):
                self.polygon2osm(osmId, poly, elem)
        print ('---')
        for transition in Output.transitionlst:
            self.transition2osm(transition)
        print ('---')
        for goal in Output.goalLst:
            self.goal2osm(goal)

    def polygon2osm(self, osmId, poly, elem = None):
        
        tags = {}
        tags.update(self.config.areaTags)
        nodeRefs = self.coords2nodeRefs(poly.exterior._get_coords(), True)
        if elem == None:
            tags = {osm.Id:osmId, 'origin':'JPSTools', 'highway':'footway', 'area':'yes'}
        else:
            for tag in elem.iter(tag = osm.Tag):
                k = tag.attrib[osm.Key]
                v = tag.attrib[osm.Value]
                tags[k] = v
        tags[jps.Id] = osmId
        for k, v in self.config.defaultMandatoryTags.items():
            if k not in tags:
                tags[k] = v
        OSMOut().addWay(Way(osmId, nodeRefs, tags))

    def transition2osm(self, transition):
        try:
            if isinstance(transition.geometry, geometry.Polygon):
                nodeRefs = self.coords2nodeRefs(transition.geometry.exterior._get_coords())
            elif isinstance(transition.geometry, geometry.LineString):
                nodeRefs = self.coords2nodeRefs(transition.geometry.coords)
        except AttributeError:
            print('not handling Transition ', transition.osmId1, transition.osmId2)
            return
        nodeRefs = list(set(nodeRefs))
        if len(nodeRefs) == 2:
            tags = {'origin': 'JPSTools', 'jupedsim': 'transition', jps.Room1: transition.osmId1,
                    jps.Room2: transition.osmId2}
            OSMOut().addTransition(Way(len(OSMOut.transitions) + 1, nodeRefs, tags))

    def goal2osm(self, goal):
        try:
            if isinstance(goal.geometry, geometry.Polygon):
                nodeRefs = self.coords2nodeRefs(goal.geometry.exterior._get_coords())
        except AttributeError:
            print('not handling Transition ', goal.tags, goal.geometry)
            return
        if len(nodeRefs) > 2:
            OSMOut().addGoal(Way(len(OSMOut.goals) + 1, nodeRefs, goal.tags))

    def coords2nodeRefs(self, coords = [], allowAdding = True):
        nodeRefs = []
        nodeRefPrevious = ''
        for coord in coords:
            lat, lon = self.config.transform.XY2WGS(coord[0], coord[1])
            nodeRef = OSMOut().getOrAddNode(coord[0], coord[1], lat, lon, self.config.errorDistance, {}, allowAdding)
            if nodeRef != nodeRefPrevious:
                nodeRefs.append(nodeRef)
            nodeRefPrevious = nodeRef
        return nodeRefs
        
    def buildOSMTree(self):
        '''
        form an xml string from all objects
        '''
        print ('---')
        
        #required attributes of the geometry element
        attribs = {}
        attribs['version'] = '0.6' 
        attribs['generator'] = 'JPSTools'
          
        osmTree = Element(OSMOut.tag, attribs)
        for node in OSMOut.nodes.values():
            outNode = SubElement(osmTree, node.tag, node.attribs)
            for tag in node.tags.items():
                SubElement(outNode, tag.tag, tag.attribs)
        
        for way in OSMOut.ways:
            self.way2subElement(osmTree, way)
        for way in OSMOut.transitions:
            self.way2subElement(osmTree, way)
        for way in OSMOut.goals:
            self.way2subElement(osmTree, way)
        self.osmTree = osmTree

    def way2subElement(self, osmTree, way):
        outWay = SubElement(osmTree, way.tag, way.attribs)
        for nodeRef in way.nodeRefs:
            SubElement(outWay, osm.NodeRef, {osm.Ref: str(nodeRef)})
        for k, v in way.tags.items():
            SubElement(outWay, osm.Tag, {osm.Key: k, osm.Value: v})
    
    def tree2xml(self, outputPath):
        '''
        writes the ElementTree geometry to a xml file
        '''
        out = tostring(self.osmTree, pretty_print=True, encoding='unicode')
        print ('---')
        #print out
        if outputPath.endswith('.osm'):
            pass
        else:
            outputPath += 'osm2jps.osm'
        try:
            f = open(outputPath, 'w')
            f.write(out)
            f.close()
            print ('output written to', outputPath)
        except Exception:
            print ('output not written!')
            
class OSMOut:
    tag = osm.Osm
    nodes = {}
    ways = []
    transitions = []
    goals = []
        
    def getOrAddNode(self, x, y, lat, lon, errorDistance, tags = {}, allowAdding = True):
        '''
        returning a node reference either from an existing node or from a newly created node
        '''
        #checking all exisitng nodes if one is the same and can be used
        pNew = geometry.Point(x, y)
        for nodeRef, node in self.nodes.items():  #iteritems():
            pOld = geometry.Point(node.x, node.y)
            if pNew.distance(pOld) < errorDistance:
                return nodeRef
        
        #creating new node
        if allowAdding:
            nodeRef = -(len(self.nodes)+1)
            node = Node(nodeRef, x, y, lat, lon, tags)
            self.nodes[nodeRef] = node
            return nodeRef
        else:
            return
        
    def addWay(self, way):
        '''
        '''
        if isinstance(way, Way):
            self.ways.append(way)
        else:
            raise Exception
        
    def addTransition(self, way):
        '''

        :param way:
        :return:
        '''
        if isinstance(way, Way) and len(way.nodeRefs) == 2:
            for transition in self.transitions:
                if set(transition.nodeRefs) == set(way.nodeRefs):
                    return
            self.transitions.append(way)
        else:
            raise Exception
        
    def addRelation(self, relation):
        pass

    def addGoal(self, way):
        '''

        :param goal:
        :return:
        '''
        if isinstance(way, Way):
            for transition in self.transitions:
                if set(transition.nodeRefs) == set(way.nodeRefs):
                    return
            self.goals.append(way)
        else:
            raise Exception
    
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
    
    def __init__(self, id, nodeRefs, tags):
        self.attribs = {}
        self.attribs[osm.Id] = str(id)
        self.attribs['version'] = '9999999'
        self.nodeRefs = nodeRefs
        self.tags = tags
    
        
        
        
