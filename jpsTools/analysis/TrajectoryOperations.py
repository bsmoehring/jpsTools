import xml.etree.ElementTree as ET

from shutil import copyfile

from Agents import Agents, Source, Counts, Area
from constants import jps
from coords import Transformation
from shapely.geometry import *
import fiona

class TrajectoryOperations():

    def __init__(self, transform, fps, timestampInterval):
        self.transform = transform
        self.fps = fps
        self.frameDivisor = fps*timestampInterval

    def getAgentsOccurences(self, trajfile, agents):

        print(self.__class__.__name__, 'getAgentOccurences', trajfile)

        assert isinstance(agents, Agents)

        file = open(trajfile)
        for event, elem in ET.iterparse(file, events=['end']):
            assert isinstance(elem, ET.Element)

            if elem.tag == jps.Frame:
                frameId = elem.attrib[jps.Traj_ID]
                frame = int(float(frameId))
                countFrameAgents = 0
                #print(elem.attrib[jps.Traj_ID])
                for agentElem in elem.iter(jps.Agent):
                    assert isinstance(agentElem, ET.Element)
                    agent_id = agentElem.attrib[jps.Traj_ID]
                    agents.agents_sources.addOccurence(agent_id, frame, float(agentElem.attrib['z']))
                    countFrameAgents += 1
                agents.counts.add_area_agent_frame(frame=frame, area_id='agentsInSim', agent_id=None, countAgents=countFrameAgents)
                elem.clear()

                #ability to test this on short runs
                #if frameId == '2000':
                #    break
            elif elem.tag == jps.FrameRate:
                frameRate = float(elem.text)


        file.close()

        return frameRate, frameId

    def agents2shape(self, trajfile, geoJsonFile, agents):

        print(self.__class__.__name__, 'agents2shape', trajfile)

        assert isinstance(agents, Agents)
        properties = {
                jps.Group_ID:'str', jps.Agent_ID:'str', jps.Time:'str', 'firstFrame':'str',
                'lastFrame':'str', 'frames':'str', 'secondsInSim':'float', 'platformFrom':'str', 'platformTo':'str',
                'firstZ':'str', 'firstChangeZ':'str', 'firstChangeZFrame':'str', 'lastChangeZ':'str',
                'lastChangeZFrame':'str', 'lastZ':'str', 'framesZ':'str', 'secondsBetweenZChange':'float'}
        for area in Counts.area_list:
            properties['area_'+area.area_id] = 'str'
        schema = {
            'geometry': 'LineString',
            'properties': properties
        }
        with fiona.open(geoJsonFile, 'w', 'ESRI Shapefile', schema) as f:

            agent_traj_dic = {}
            sources_dic = agents.agents_sources.sourcesDic
            assert isinstance(sources_dic, dict)
            firstFrames = []
            lastFrames = []
            agent_id_int_list = [int(agent_id) for agent_id, source in sources_dic.items()]
            for agent_id in sorted(agent_id_int_list):
                source = sources_dic[str(agent_id)]
                assert isinstance(source, Source)

                agent_traj_dic[str(agent_id)] = AgentTraj(agent_id)
                firstFrames.append(source.firstFrame)
                lastFrames.append(source.lastFrame)
                if len(agent_traj_dic)>=1000:
                    self.traj2points(
                        trajfile, firstFrames, lastFrames, agents, agent_traj_dic, f
                    )
            self.traj2points(
                trajfile, firstFrames, lastFrames, agents, agent_traj_dic, f
            )



    def traj2points(self, trajfile, firstFrames, lastFrames, agents, agent_traj_dic, f):

        firstFrame = min(firstFrames)
        lastFrame = max(lastFrames)

        print(self.__class__.__name__, 'traj2points', firstFrame, lastFrame, trajfile)

        file = open(trajfile)

        for event, elem in ET.iterparse(file, ['start', 'end']):
            assert isinstance(elem, ET.Element)
            if event == 'start':
                continue

            elif elem.tag == jps.Frame:
                frameId = elem.attrib[jps.Traj_ID]
                frame = int(float(frameId))
                seconds = frame / self.fps

                if frame % self.frameDivisor == 0 and frame >= firstFrame and frame <= lastFrame:
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
                        agentElem.clear()

                elem.clear()
                # ability to test this on short runs
                if frame > lastFrame:
                    break
        file.close()
        firstFrames.clear()
        lastFrames.clear()
        agent_traj_dic.clear()

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
            # print(agent_id2, linestring)
        agent_traj_dic.clear()
        firstFrames.clear()
        lastFrames.clear()

    def assign_areas(self, trajfile, agents, counts):

        print(self.__class__.__name__, 'assign_areas', trajfile)

        file = open(trajfile)
        assert isinstance(agents, Agents)

        for event, elem in ET.iterparse(file, ['end']):
            assert isinstance(elem, ET.Element)
            if elem.tag == jps.Frame:
                frameId = elem.attrib[jps.Traj_ID]
                frame = int(float(frameId))
                seconds = frame / self.fps

                if frame % self.frameDivisor == 0:
                    #print(frame)
                    for agentElem in elem.iter(jps.Agent):
                        agent_id = agentElem.attrib[jps.Traj_ID]
                        x = float(agentElem.attrib['x'])
                        y = float(agentElem.attrib['y'])
                        z = float(agentElem.attrib['z'])
                        for area in counts.area_list:
                            if z == area.z and x > area.xmin and x < area.xmax and y > area.ymin and y < area.ymax:
                                counts.add_area_agent_frame(frame=frame, area_id=area.area_id, agent_id=agent_id, countAgents=None)
                                if agent_id not in area.agents_list:
                                    area.agents_list.append(agent_id)
                        agentElem.clear()
                elem.clear()
        file.close()

    def filter_traj_by_areas(self, trajfile, counts):

        print(self.__class__.__name__, 'filter_traj_by_areas', trajfile)
        #iterate over areas
        for area in counts.area_list:
            print(area.area_id, len(area.agents_list))

            newFile = trajfile[:-4]+'selected_area_'+area.area_id+'.xml'
            #copyfile(trajfile, newFile)
            with open(newFile, "wb") as f:
                f.write('<trajectories>'.encode())
                for event, elem in ET.iterparse(trajfile, events=['end']):
                    if elem.tag == jps.Agent:
                        continue
                    if elem.tag == jps.Frame:
                        for agentElem in elem.iterfind(jps.Agent):
                            if agentElem.attrib[jps.Traj_ID] not in area.agents_list:
                                elem.remove(agentElem)
                        f.write(ET.tostring(elem))
                        elem.clear()
                    elif elem.tag == 'header':
                        f.write(ET.tostring(elem))
                        elem.clear()
                    elif elem.tag == 'geometry':
                        f.write(ET.tostring(elem))
                        elem.clear()
                    elif elem.tag == 'AttributeDescription':
                        f.write(ET.tostring(elem))
                        elem.clear()
                f.write('</trajectories>'.encode())


    def getelements(self, filename_or_file):

        for event, elem in ET.iterparse(filename_or_file, events=('start', 'end')):
            yield event, elem
            elem.clear()  # free memory

class AgentTraj:

    def __init__(self, agent_id):

        self.agent_id = agent_id
        self.points = []

    def addPoint(self, lat, lon, z, seconds):
        self.points.append((lon, lat, z, seconds))
