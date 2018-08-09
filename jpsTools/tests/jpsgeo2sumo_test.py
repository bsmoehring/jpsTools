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
            sumo_net.addNode(id=id, coord=coord, type=subroom.attribs[jps.Class])

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
        if '-1_-1' in id:
            continue
        sumo_net.addEdge(id=id, fromID=fromID, toID=toID, prio=1, function='walkingarea', name=id)
        edge = sumo_net.getEdge(id)
        sumo_net.addLane(edge=edge, length=0.01, speed=1.39)

    return geo, sumo_net


            # elif num_transcross == 2:
            #     #TODO: subroom2edge
            #     pass
            # elif num_transcross == 1:
            #     #TODO: think about it
            #     pass
            # else:
            #     raise Exception

def sumo_net2plainxml(geo=Geometry, sumo_net=Net(), outputfile=str):

    with open(outputfile+'.nod.xml', 'w') as f:

        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<nodes>\n')
        for node in sumo_net.getNodes():
            assert isinstance(node, Node)
            print(node.getID())
            print(node.getCoord())
            f.writelines(
                '\t<node id="%s" x="%s" y="%s" type="%s"/>\n'
                % (node.getID(), node.getCoord()[0], node.getCoord()[1], node.getType())
                )
        f.write('</nodes>')

    with open(outputfile+'.edg.xml', 'w') as f:

        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<edges>\n')

        for edge in sumo_net.getEdges():
            assert isinstance(edge, Edge)
            jps_id = edge.getID().split('/')[0]
            shape = ""
            if '_' in jps_id:
                #crossing
                room_id = jps_id.split('_')[0]
                crossing_id = jps_id.split('_')[1]
                crossing = geo.rooms[room_id].crossings[crossing_id]
                shape = crossing.getShape4Sumo()
            else:
                #transition
                transition = geo.transitions[jps_id]
                shape = transition.getShape4Sumo()
            f.write(
                '\t<edge id="%s" from="%s" to="%s" width="%s" numLanes="1" speed="%s" spreadType="%s" length="%s" allow="pedestrian" shape="%s"/>\n'
                % (edge.getID(), edge.getFromNode().getID(), edge.getToNode().getID(), 2, 1.34, 'center', 0.01, shape)
            )
        f.write('</edges>\n')

    with open(outputfile+'.con.xml', 'w') as f:

        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<connections>\n')

        for node in sumo_net.getNodes():
            assert isinstance(node, Node)
            edges = ''
            for edge in node.getIncoming() + node.getOutgoing():
                assert isinstance(edge, Edge)
                if edges != '':
                    edges += ' '
                edges += edge.getID()
            shape = geo.rooms[node.getID().split('_')[0]].subrooms[node.getID().split('_')[1]].getShape4Sumo()
            f.write(
                '\t<walkingArea node="%s" type="%s" edges="%s" shape="%s"/>\n'
                % (node.getID(), node.getType(), edges, shape)
            )


        f.write('</connections>\n')



if      __name__ == "__main__":

    geo, sumo_net=jps2sumo_net('/media/bsmoehring/Data/stuff/jupedsim/jpsTools/jpsTools/osm2jps/resources/jps_geo.xml')
    sumo_net2plainxml(geo, sumo_net, '/media/bsmoehring/Data/stuff/jupedsim/jpsTools/jpsTools/osm2jps/resources/jps2sumo')