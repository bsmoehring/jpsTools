import xml.etree.ElementTree as ET

from Agents import Agents, Source
from constants import jps
from coords import Transformation
from shapely.geometry import *
import fiona

class TrajectoryOperations():

    def __init__(self, transform):
        self.transform = transform

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
                    agents.agents_sources.addOccurence(agentElem.attrib[jps.Traj_ID], frame, float(agentElem.attrib['z']))
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

    def agents2geojson(self, trajfile, geoJsonFile, agents, fps, timestampInterval):

        frameDivisor = fps*timestampInterval

        assert isinstance(agents, Agents)
        schema = {
            'geometry': 'LineString',
            'properties': {
                jps.Group_ID:'str', jps.Agent_ID:'str', jps.Time:'str', 'firstFrame':'str',
                'lastFrame':'str', 'frames':'str', 'secondsInSim':'float', 'platformFrom':'str', 'platformTo':'str',
                'firstZ':'str', 'firstChangeZ':'str', 'firstChangeZFrame':'str', 'lastChangeZ':'str',
                'lastChangeZFrame':'str', 'lastZ':'str', 'secondsBetweenZChange':'float'},
        }
        with fiona.open(geoJsonFile, 'w', 'ESRI Shapefile', schema) as f:
            i = 0
            for agent_id, source in agents.agents_sources.sourcesDic.items():
                assert isinstance(source, Source)
                firstFrame = source.firstFrame
                lastFrame = source.lastFrame

                traj = AgentTraj(agent_id)
                file = open(trajfile)

                for event, elem in ET.iterparse(file, ['start', 'end']):
                    assert isinstance(elem, ET.Element)
                    if event == 'start':
                        continue

                    elif elem.tag == jps.Frame:
                        frameId = elem.attrib[jps.Traj_ID]
                        frame = int(float(frameId))

                        if frame % frameDivisor and frame >= firstFrame and frame <= lastFrame:

                            for agentElem in elem.iter(jps.Agent):
                                assert isinstance(agentElem, ET.Element)
                                if agentElem.attrib[jps.Traj_ID] == agent_id:
                                    lat, lon = self.transform.XY2WGS(
                                        float(agentElem.attrib['x']),
                                        float(agentElem.attrib['y'])
                                    )
                                    traj.addPoint(
                                        lat,
                                        lon,
                                        float(agentElem.attrib['z']),
                                        frame/fps
                                    )
                            elem.clear()

                        elem.clear()
                        # ability to test this on short runs
                        if frame >= 1000:
                            break
                linestring = LineString(traj.points)
                f.write({
                    'properties':source.getAttribDic(),
                    'geometry':mapping(linestring)
                })

                print(agent_id, linestring)
                file.close()
                i +=1
                if i>3:
                    break


class AgentTraj:

    def __init__(self, agent_id):

        self.agent_id = agent_id
        self.points = []

    def addPoint(self, lat, lon, z, seconds):
        self.points.append((lon, lat, z))

