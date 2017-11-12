'''
Created on 11.11.2017

@author: user
'''
from coords import Transformation
import jpsElements
from main import Input
from constants import osm, jps
from config import Config
from shapely.geometry import Polygon, LineString
from shapely.geometry.base import CAP_STYLE, JOIN_STYLE

class ElementHandler(object):
    '''
    classdocs
    '''
    def __init__(self):
        self.transform = Transformation(Input.tree.find(osm.Bounds))

    def handle(self, elem):
        if elem.tag == osm.Way:
            #Way
            self.way2polygon(elem)
        elif elem.tag == osm.Relation:
            #Relation
            print 'Element:', elem.attrib[osm.Id], '--> Relation'
            wayRefs = []
            for member in elem.iter(tag=osm.Member):
                if member.attrib.get(osm.Type) == osm.Way:
                    if member.attrib.get(osm.Role) == osm.Outer:
                        print 'Outer Member -> Way'
                        wayRefs.append(member.attrib.get(osm.Ref))
                    elif member.attrib[osm.Role] == osm.Inner:
                        wayRef = member.attrib.get(osm.Ref)
                        print 'Inner Member -> Not handled yet!'
            if wayRefs:
                for way in Input.tree.iter(tag=osm.Way):
                    if way.attrib.get(osm.Id) in wayRefs:
                        self.way2polygon(way)
        else:
            print 'Element:', elem.attrib[osm.Id], 'is a:', elem.tag, '. How to handle this?' 
                
                
    def nodeRefs2XY(self, nodeRefs):
        XYList = []
        for nodeRef in nodeRefs:
            try:
                node = Input.nodes[nodeRef]
                lat = (node.attrib[osm.Lat])
                lon = (node.attrib[osm.Lon])
                x, y = self.transform.WGSToXY(lat, lon)
                XYList.append((x, y))
            except KeyError:
                print nodeRef, 'is not in the nodes list. ->OSM inconsistency?'
        return XYList
    
    def way2polygon(self, elem):
        '''
        translate osm way to a shapely.geometry.polygon in order to to easily manipulate its shape.
        '''
        print  'Element:', elem.attrib[osm.Id], '--> Way'
        #area?
        area = False
        nodeRefs = []
        for child in elem:
            if child.tag == osm.Tag: 
                try:
                    if child.attrib[osm.Value] in Config.areaTags[child.attrib[osm.Key]]:
                        area = True
                except KeyError:
                    pass
            if child.tag == osm.NodeRef:
                nodeRefs.append(child.attrib[osm.Ref])  
        XYList = self.nodeRefs2XY(nodeRefs)
        print 'NodeRefs:', nodeRefs
        print 'Coordinates:', XYList
        if area:
            #check if first and last nodes are the same
            if len(nodeRefs) > 2 and nodeRefs[0] == nodeRefs [-1]:
                #polygon
                poly = Polygon(XYList)
            else:
                #area == yes, but no polygon structure
                print  elem.attrib[osm.Id], 'has wrong tags. Area=yes but first and last node references are not the same or less than 3 nodes'
                #continue as linestring?
        else:
            #LineString
            print elem.attrib[osm.Id], 'is a LineString and needs to be buffered to create a Polygon.'
            ls = LineString(XYList)
            #polygon from linestring
            poly = ls.buffer(Config.stanardWidth/2, cap_style=CAP_STYLE.square, join_style=JOIN_STYLE.mitre, mitre_limit=Config.stanardWidth)
        self.polygon2jps(poly, elem)
        
    
    def polygon2jps(self, poly, elem):
        '''
        translate polygon to jps Elements
        '''
        print poly
        jpsRoom = jpsElements.Room(elem.attrib.get(osm.Id), elem.attrib.get(osm.Level), 'hall')
        jpsSubroom = jpsElements.Subroom()
        jpsPoly = jpsElements.Polygon()
        for coord in poly.exterior._get_coords():
            jpsVertex = jpsElements.Vertex(str(coord[0]), str(coord[1]))
            jpsPoly.addVertex(jpsVertex)
        jpsSubroom.addPolygon(jpsPoly)
        jpsRoom.addSubroom(jpsSubroom)
        jpsElements.Geometry().addRoom(jpsRoom)
            
                