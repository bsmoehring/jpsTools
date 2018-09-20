from Agents import Agents, Source, Group
from sumolib.net import *
import random

def main(input):

    print('###')
    print(input[0])
    inputfolder = input[0]

    inputIni = inputfolder + 'jps_ini.xml'

    xmin = 799093.3516501468
    ymin = 5828024.700676445

    agents = Agents(inputIni)
    sumo_net = readNet('/media/bsmoehring/Data/stuff/jupedsim/jpsTools/jpsTools/osm2jps/resources/jps2sumo.net.xml')

    with open('/media/bsmoehring/Data/stuff/jupedsim/jpsTools/jpsTools/osm2jps/resources/' + 'trips.trips.xml', 'w') as f:

        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<routes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/routes_file.xsd">\n')

        for source in sorted(agents.agents_sources.sourcesDic.values(), key = lambda source: int(source.time)):
            assert isinstance(source, Source)
            group = source.getGroup()
            assert isinstance(group, Group)

            from_node = sumo_net.getNode(group.room_id + '_' + group.subroom_id)
            assert isinstance(from_node, Node)
            from_edge = random.choice(from_node.getIncoming()+from_node.getOutgoing())

            to_id = group.goal_id[:2] + '_' + group.goal_id[2:]
            if to_id[0] == '0':
                to_id = to_id[1:]
            to_node = sumo_net.getNode(to_id)
            assert isinstance(to_node, Node)
            to_edge = random.choice(to_node.getIncoming()+to_node.getOutgoing())

            s = '\t<person id ="%s" depart = "%s">\n\t\t<walk from="%s" to= "%s"/>\n\t</person>\n' % (source.agent_id, source.time+'.00', from_edge.getID(), to_edge.getID())
            print(s)
            f.write(s)

        f.write('</routes>')

if __name__ == "__main__":
    input = []
    input.append(('/media/bsmoehring/Data/wichtiges/tuberlin/masterarbeit/runs/0_ipfDemandBasic/', {'10312': '11', '4760': '21', '9184': '31', '14000': '15'}))
    #input.append(('/media/bsmoehring/Data/wichtiges/tuberlin/masterarbeit/runs/1_ipfDemandProg1/', {'12800': '11', '13840': '21', '8632': '31', '14000': '15'}))
    #input.append(('/media/bsmoehring/Data/wichtiges/tuberlin/masterarbeit/runs/2_ipfDemandProg2/', {'3728': '11', '10640': '21', '5824': '31', '14000': '15'}))
    #input.append(('/media/bsmoehring/Data/wichtiges/tuberlin/masterarbeit/tests/report/smalltraj/', {}))

    for s in input:
        main(s)