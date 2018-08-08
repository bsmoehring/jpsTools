import geometry_reader
from jps_constants import jps
from geometry import Geometry, Room, Subroom, Crossing, Transition
from sumolib.net import *

def jps2sumo_net(inputfile):

    geo = geometry_reader.read_jps_geometry(inputfile)
    assert isinstance(geo, Geometry)

    sumo_net = Net()

    for room in geo.rooms.values():
        room_id = room.attribs[jps.Id]
        assert isinstance(room, Room)

        for subroom in room.subrooms.values():
            assert isinstance(subroom, Subroom)
            id = room_id+'_'+subroom.attribs[jps.Id]
            coord = subroom.getCenterCoord()
            sumo_net.addNode(id=id, coord=coord)

        for crossing in room.crossings.values():
            assert isinstance(crossing, Crossing)
            id = room_id+'_'+crossing.attribs[jps.Id]+'/'+room_id+'_'+crossing.attribs[jps.Subroom1]+'/'+room_id+'_'+crossing.attribs[jps.Subroom2]
            fromID = room_id+'_'+crossing.attribs[jps.Subroom1]
            toID = room_id+'_'+crossing.attribs[jps.Subroom2]
            sumo_net.addEdge(id=id, fromID=fromID, toID=toID, prio=1, function='walkingarea', name=id)
            edge = sumo_net.getEdge(id=id)
            sumo_net.addLane(edge=edge, length=0.01, speed=1.39)

    for transition in geo.transitions.values():
        transition_id = transition.attribs[jps.Id]
        assert isinstance(transition, Transition)
        fromID = transition.attribs[jps.Room1]+'_'+transition.attribs[jps.Subroom1]
        toID = transition.attribs[jps.Room2]+'_'+transition.attribs[jps.Subroom2]
        id = transition_id+'/'+fromID+'/'+toID
        # no transitions to universe
        if '-1_' in id:
            continue
        sumo_net.addEdge(id=id, fromID=fromID, toID=toID, prio=1, function='walkingarea', name=id)
        edge = sumo_net.getEdge(id)
        sumo_net.addLane(edge=edge, length=0.01, speed=1.39)

    return sumo_net


            # elif num_transcross == 2:
            #     #TODO: subroom2edge
            #     pass
            # elif num_transcross == 1:
            #     #TODO: think about it
            #     pass
            # else:
            #     raise Exception

def sumo_net2xml(sumo_net=Net(), outputfile=str):

    with open(outputfile, 'w') as f:

        def write(s):
            s

        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<net version="0.27" walkingareas="true" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/net_file.xsd">\n')
        for node in sumo_net.getNodes():
            assert isinstance(node, Node)
            incLanes = ''
            for incEdge in node.getIncoming():
                assert isinstance(incEdge, Edge)
                if incLanes != '':
                    incLanes += ' '
                for lane in incEdge.getLanes():
                    assert isinstance(lane, Lane)
                    incLanes += lane.getID()
            print(node.getID())
            print(node.getCoord())
            f.writelines(
                '\t<junction id="%s" x="%s" y="%s" incLanes="%s"/>\n'
                % (node.getID(), node.getCoord()[0], node.getCoord()[1], incLanes)
                )

        for edge in sumo_net.getEdges():
            assert isinstance(edge, Edge)
            f.write(
                '\t<edge id="%s" from="%s" to="%s">\n'
                % (edge.getID(), edge.getFromNode().getID(), edge.getToNode().getID())
            )
            for lane in edge.getLanes():
                assert isinstance(lane, Lane)
                f.write(
                    '\t\t<lane id="%s" index="%s" allow="pedestrian" speed="%s" length="%s" width="%s"/>\n'
                    % (lane.getID(), lane.getIndex(), lane.getSpeed(), lane.getLength(), 2)
                )
            f.write('\t</edge>\n')
        f.write('</net>\n')


if      __name__ == "__main__":

    sumo_net=jps2sumo_net('/media/bsmoehring/Data/stuff/jupedsim/jpsTools/jpsTools/osm2jps/resources/jps_geo.xml')
    sumo_net2xml(sumo_net, '/media/bsmoehring/Data/stuff/jupedsim/jpsTools/jpsTools/osm2jps/resources/jps2sumo.net.xml')