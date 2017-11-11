'''
Created on 07.11.2017

@author: bsmoehring
'''


class osm(object):
    '''
    This class aims to store required strings to parse OSM data
    '''
    Id = 'id'
    Node = 'node'
    Way = 'way'
    Relation = 'relation'
    Ref = 'ref'
    NodeRef = 'nd'
    Lat = 'lat'
    Lon ='lon'
    Bounds = 'bounds'
    MinLat = 'minlat'
    MinLon = 'minlon'
    Level = 'level'
    Member = 'member'
    Type = 'type'
    Role = 'role'
    Outer = 'outer'
    Inner = 'inner'
    Key = 'k'
    Value = 'v'
        
class jps(object):
    '''
    This class aims to store required strings for the jps input files
    '''
    Geometry = 'geometry'
    Rooms = 'rooms'
    Room = 'room'
    Subroom = 'subroom'
    Polygon = 'polygon'
    Vertex = 'vertex'
    Id = 'id'
    Caption = 'caption'
    PX = 'px'
    PY = 'py'
    Wall = 'wall'
    OriginalId = 'originalId'
    Transition = 'transition' 
    Type = 'type'
    Room1 = 'room1_id'
    Subroom1 = 'subroom1_id'
    Room2 = 'room2_id'
    Subroom2 = 'subroom2_id'
    
class geometryAttribs(object):
    '''
    required attributes of the geometry element
    '''
    attribs = {}
    attribs['version'] = '0.8' 
    attribs['caption'] = 'second life' 
    attribs['unit'] = 'm'
    #attribs['xmlns:xsi'] = 'http://www.w3.org/2001/XMLSchema-instance'
    #attribs['xsi:noNamespaceSchemaLocation'] = '../../xsd/jps_geometry.xsd'  
    