import geometry_reader
from jps_constants import jps
from geometry import Geometry, Room, Subroom, Crossing, Transition
from sumolib.net import *
from scipy.spatial import distance

def jps2sumo_net(inputfile):

    #read jps geometry.xml
    geo = geometry_reader.read_jps_geometry(inputfile)
    assert isinstance(geo, Geometry)

    #create sumo network
    sumo_net = Net()


    for room in geo.rooms.values():
        room_id = room.attribs[jps.Id]
        assert isinstance(room, Room)

        #add all subrooms as nodes
        for subroom in room.subrooms.values():
            assert isinstance(subroom, Subroom)
            if room_id != subroom.attribs[jps.Room]:
                raise Exception
            id = subroom.attribs[jps.Room]+'_'+subroom.attribs[jps.Subroom]
            coord = subroom.getCenterCoord()
            #check if subroom has exactly 2 crossings/transitions
            # if subroom.attribs[jps.Class] in [jps.Stair, jps.Escalator_up, jps.Escalator_down] and subroom.getNumOfTransCross() == 2:
            if subroom.attribs[jps.Class] in [jps.Escalator_up, jps.Escalator_down]:
                trans_cross_lst = subroom.getTransCrossLst()
                for trans_cross in trans_cross_lst:
                    if isinstance(trans_cross, Transition):
                        del geo.transitions[trans_cross.attribs[jps.Id]]
                    else:
                        raise Exception
            elif len(subroom.polygons) == 2 and len(subroom.getTransCrossLst()) == 2:
                neighbours =  subroom.getNeighbouringSubroomLst(geo)
                fromID = neighbours[0].attribs[jps.Room]+'_'+neighbours[0].attribs[jps.Subroom]
                toID = neighbours[1].attribs[jps.Room]+'_'+neighbours[1].attribs[jps.Subroom]

                trans_cross_lst = subroom.getTransCrossLst()
                length = distance.euclidean(trans_cross_lst[0].getCenterCoord(), trans_cross_lst[1].getCenterCoord())

                sumo_net.addEdge(id=id, fromID=fromID, toID=toID, prio=1, function=subroom.attribs[jps.Class], name=jps.Subroom)
                edge = sumo_net.getEdge(id=id)
                edge.shape = '%s,%s %s,%s' % (trans_cross_lst[0].getCenterCoord()+trans_cross_lst[1].getCenterCoord())
                edge.width = sum(trans_cross.getWidth() for trans_cross in trans_cross_lst)/len(trans_cross_lst)
                sumo_net.addLane(edge=edge, length=length, speed=1.39)
                #remove the two neighbouring crossings and transitions from future handling
                for trans_cross in trans_cross_lst:
                    if isinstance(trans_cross, Crossing):
                        del room.crossings[trans_cross.attribs[jps.Id]]
                    elif isinstance(trans_cross, Transition):
                        del geo.transitions[trans_cross.attribs[jps.Id]]
                    else:
                        raise Exception
            else:
                sumo_net.addNode(id=id, coord=coord, type=subroom.attribs[jps.Class])
                node = sumo_net.getNode(id=id)
                node.shape = subroom.getShape4Sumo()

        #add all crossings as edges
        for crossing in room.crossings.values():
            assert isinstance(crossing, Crossing)
            id = room_id+'_'+crossing.attribs[jps.Id]+'/'+room_id+'_'+crossing.attribs[jps.Subroom1]+'/'+room_id+'_'+crossing.attribs[jps.Subroom2]
            fromID = room_id+'_'+crossing.attribs[jps.Subroom1]
            toID = room_id+'_'+crossing.attribs[jps.Subroom2]
            sumo_net.addEdge(id=id, fromID=fromID, toID=toID, prio=1, function='walkingarea', name=jps.Crossing)
            edge = sumo_net.getEdge(id=id)
            edge.shape = crossing.getShape4Sumo()
            edge.width = crossing.getWidth()
            sumo_net.addLane(edge=edge, length=0.01, speed=1.39)

    #add all transitions as edges
    for transition in geo.transitions.values():
        transition_id = transition.attribs[jps.Id]
        assert isinstance(transition, Transition)
        fromID = transition.attribs[jps.Room1]+'_'+transition.attribs[jps.Subroom1]
        toID = transition.attribs[jps.Room2]+'_'+transition.attribs[jps.Subroom2]
        #transition id creation
        id = transition_id+'/'+fromID+'/'+toID
        # no transitions to universe
        if '-1_-1' in id:
            continue
        sumo_net.addEdge(id=id, fromID=fromID, toID=toID, prio=1, function='walkingarea', name=jps.Crossing)
        edge = sumo_net.getEdge(id)
        edge.shape = transition.getShape4Sumo()
        edge.width = transition.getWidth()
        sumo_net.addLane(edge=edge, length=0.01, speed=1.39)

    return geo, sumo_net


def sumo_net2plainxml(geo=Geometry, sumo_net=Net(), outputfile=str):

    with open(outputfile+'.nod.xml', 'w') as f:

        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<nodes>\n')
        f.write('\t<location netOffset="-392060.63039125846,-5820073.572218239" origBoundary="13.40914476019,52.5200685,13.4155947,52.5225964" convBoundary="0,0,443.77040196873713,271.53244863078" projParameter="+proj=utm +zone=32 +ellps=WGS84 +datum=WGS84 +units=m +no_defs"/>\n')

        for node in sumo_net.getNodes():
            assert isinstance(node, Node)
            print(node.getID())
            print(node.getCoord())
            f.writelines(
                '\t<node id="%s" x="%s" y="%s" type="%s" shape="%s"/>\n'
                % (node.getID(), node.getCoord()[0], node.getCoord()[1], node.getType(), node.shape)
                )
        f.write('</nodes>')

    with open(outputfile+'.edg.xml', 'w') as f:

        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<edges>\n')

        for edge in sumo_net.getEdges():
            assert isinstance(edge, Edge)
            f.write(
                '\t<edge id="%s" from="%s" to="%s" width="%s" numLanes="1" speed="%s" spreadType="%s" allow="pedestrian" shape="%s">\n'
                % (edge.getID(), edge.getFromNode().getID(), edge.getToNode().getID(), edge.width, 1.34, 'center', edge.shape)
            )
            f.write(
                '\t\t<lane index="0" shape="%s"/>\n'
                % (edge.shape)
            )
            f.write('\t</edge>\n')
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
            f.write(
                '\t<walkingArea node="%s" type="%s" edges="%s" shape="%s"/>\n'
                % (node.getID(), node.getType(), edges, node.shape)
            )


        f.write('</connections>\n')



if      __name__ == "__main__":

    geo, sumo_net=jps2sumo_net('/media/bsmoehring/Data/stuff/jupedsim/jpsTools/jpsTools/osm2jps/resources/jps_geo.xml')
    sumo_net2plainxml(geo, sumo_net, '/media/bsmoehring/Data/stuff/jupedsim/jpsTools/jpsTools/osm2jps/resources/jps2sumo')