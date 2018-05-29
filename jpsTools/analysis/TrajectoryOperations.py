import xml.etree.ElementTree as ET

import sys

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
                #print(elem.attrib[jps.Traj_ID])
                for agentElem in elem.iter(jps.Agent):
                    assert isinstance(agentElem, ET.Element)
                    agents.agents_sources.addOccurence(agentElem.attrib[jps.Traj_ID], frame, float(agentElem.attrib['z']))
                    countFrameAgents += 1
                agents.frame_statistics.agentsPerFrameDic[frameId] = countFrameAgents
                elem.clear()

                #ability to test this on short runs
                #if frameId == '2000':
                #    break
            elif elem.tag == jps.FrameRate:
                frameRate = float(elem.text)


        file.close()

        return frameRate, frameId

    def agents2geojson(self, trajfile, geoJsonFile, agents, fps, timestampInterval):

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

            agent_traj_dic = {}
            sources_dic = agents.agents_sources.sourcesDic
            assert isinstance(sources_dic, dict)
            firstframes = []
            lastframes = []
            agent_id_int_list = [int(agent_id) for agent_id, source in sources_dic.items()]
            for agent_id in sorted(agent_id_int_list):
                source = sources_dic[str(agent_id)]
                assert isinstance(source, Source)

                agent_traj_dic[str(agent_id)] = AgentTraj(agent_id)
                firstframes.append(source.firstFrame)
                lastframes.append(source.lastFrame)
                if len(agent_traj_dic)>=1000:
                    self.traj2shape(
                        trajfile, fps, timestampInterval, min(firstframes), max(lastframes), agent_traj_dic
                    )
                    for agent_id2, traj in agent_traj_dic.items():
                        if len(traj.points) == 0:
                            continue
                        elif len(traj.points) == 1:
                            traj.points.append(traj.points[0])
                        linestring = LineString(traj.points)
                        f.write({
                            'properties': agents.agents_sources.sourcesDic[agent_id2].getAttribDic(),
                            'geometry': mapping(linestring)
                        })

                        #print(agent_id2, linestring)
                    agent_traj_dic = {}
                    firstframes = []
                    lastframes = []


    def traj2shape(self, trajfile, fps, timestampInterval, firstFrame, lastFrame, agent_traj_dic={}):

        frameDivisor = fps*timestampInterval

        file = open(trajfile)

        for event, elem in ET.iterparse(file, ['start', 'end']):
            assert isinstance(elem, ET.Element)
            if event == 'start':
                continue

            elif elem.tag == jps.Frame:
                frameId = elem.attrib[jps.Traj_ID]
                frame = int(float(frameId))
                seconds = frame / fps

                if frame % frameDivisor == 0 and frame >= firstFrame and frame <= lastFrame:
                    #print(frame)
                    for agentElem in elem.iter(jps.Agent):
                        agent_id = agentElem.attrib[jps.Traj_ID]
                        if agent_id in agent_traj_dic.keys():
                            lat, lon = self.transform.XY2WGS(
                                float(agentElem.attrib['x']),
                                float(agentElem.attrib['y'])
                            )
                            z = float(agentElem.attrib['z'])
                            agent_traj_dic[agent_id].addPoint(lat, lon, z, seconds)
                    elem.clear()

                elem.clear()
                # ability to test this on short runs
                if frame > lastFrame:
                    break
        file.close()

class AgentTraj:

    def __init__(self, agent_id):

        self.agent_id = agent_id
        self.points = []

    def addPoint(self, lat, lon, z, seconds):
        self.points.append((lon, lat, z))

