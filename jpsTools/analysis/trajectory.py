import xml.etree.ElementTree as ET

from agents import Agents
from constants import jps

class Trajectory():

    def getAgentsOccurences(self, trajfile, agents):

        assert isinstance(agents, Agents)

        file = open(trajfile)
        for event, elem in ET.iterparse(file, ['start', 'end']):
            assert isinstance(elem, ET.Element)

            if event == 'start':
                continue

            if elem.tag == jps.Frame:
                frameId = elem.attrib[jps.Traj_ID]
                frame = int(float(frameId))
                countFrameAgents = 0
                print(elem.attrib[jps.Traj_ID])
                for agentElem in elem.iter(jps.Agent):
                    assert isinstance(agentElem, ET.Element)
                    agents.agents_sources.addOccurence(agentElem.attrib[jps.Traj_ID], frame)
                    countFrameAgents += 1
                agents.frame_statistics.agentsPerFrameDic[frameId] = countFrameAgents
                elem.clear()

                #ability to test this on short runs
                if frameId == '1000':
                    break
            elif elem.tag == jps.FrameRate:
                frameRate = float(elem.text)


        file.close()

        return frameRate, frameId