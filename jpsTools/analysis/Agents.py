import xml.etree.ElementTree as ET
from constants import jps

class Agents():

    def __init__(self, inifile=None):

        self.agents_distribution = Agents_Distribution()
        self.agents_sources = Agents_Sources()
        self.counts = Counts()

        if isinstance(inifile, str):
            file = open(inifile)
            for event, elem in ET.iterparse(file, ['start', 'end']):
                assert isinstance(elem, ET.Element)

                if event == 'start':
                    continue

                if elem.tag == 'agents_distribution':
                    for groupElem in elem.iter(jps.Group):
                        assert isinstance(groupElem, ET.Element)
                        self.agents_distribution.addGroup(Group(groupElem.attrib))
                    elem.clear()

                if elem.tag == 'agents_sources':
                    print(event, elem.tag)
                    for sourceElem in elem.iter(jps.Source):
                        assert isinstance(sourceElem, ET.Element)
                        self.agents_sources.addSource(Source(sourceElem.attrib))
                    elem.clear()
                if elem.tag == 'trajectories':
                    fps = int(elem.attrib['fps'])
                    print(event, elem.tag, fps)
                    self.fps = fps
                    elem.clear()
            file.close()

        print('groups: ', len(self.agents_distribution.groupsDic))
        print('agents: ', len(self.agents_sources.sourcesDic))

    def clear(self):
        self.agents_distribution.groupsDic.clear()
        self.agents_sources.sourcesDic.clear()
        self.counts.area_list.clear()
        self.counts.agentsPerFrameDic.clear()
        self.counts.time_area_agents_dic.clear()

class Agents_Distribution:

    groupsDic = {}

    def addGroup(self, group):
        self.groupsDic[group.group_id] = group

class Agents_Sources:

    sourcesDic = {}

    def addSource(self, source):
        self.sourcesDic[source.agent_id] = source

    def addOccurence(self, agent_id, frame, z):

        source = self.sourcesDic[agent_id]
        assert isinstance(source, Source)
        if source.firstFrame == None:
            source.firstFrame = frame
            source.firstZ = z
        #get first change in z
        if source.firstChangeZ == None and source.firstZ != z:
            source.firstChangeZ = z
            source.firstChangeZFrame = frame
        #keep last z change
        elif source.lastChangeZ == None and source.lastZ != z:
            source.lastChangeZ = z
            source.lastChangeZFrame = frame
        source.lastFrame = frame
        source.lastZ = z


class Group:

    def __init__(self, attribDic = {}):

        self.caption = attribDic[jps.Caption]
        self.goal_id = attribDic[jps.Goal_ID]
        self.group_id = attribDic[jps.Group_ID]
        self.room_id = attribDic[jps.Room_ID]
        self.subroom_id = attribDic[jps.Subroom_ID]

        #self.platformFrom = getPlatformFrom(self.room_id, self.subroom_id)
        #self.platformTo = getPlatformTo(self.goal_id)

    def getAgents(self):
        '''
        get all sources of this group_id
        :return:
        '''

        agents = {}
        for source in Agents_Sources.sourcesDic.items():
            assert isinstance(source, Source)
            if source.group_id == self.group_id:
                agents[source.agent_id] = source

        return agents

class Source:

    def __init__(self, attribDic = {}):

        self.group_id = attribDic[jps.Group_ID]
        self.agent_id = attribDic[jps.Agent_ID]
        self.time = attribDic[jps.Time]
        self.firstFrame = None
        self.lastFrame = None
        self.frames = None
        self.secondsInSim = None
        self.platformFrom = None
        self.platformTo = None
        self.firstZ = None
        self.firstChangeZ = None
        self.firstChangeZFrame = None
        self.lastChangeZ = None
        self.lastChangeZFrame = None
        self.lastZ = None
        self.secondsBetweenZChange = None

    def getGroup(self):
        '''
        get Group of this Source
        :return:
        '''

        return Agents_Distribution().groupsDic[self.group_id]

    def getAttribDic(self):
        attribDic = {}
        attribDic[jps.Group_ID]     = self.group_id
        attribDic[jps.Agent_ID]     = self.agent_id
        attribDic[jps.Time]         = self.time
        attribDic['firstFrame'] = self.firstFrame
        attribDic['lastFrame'] = self.lastFrame
        attribDic['frames'] = self.frames
        attribDic['secondsInSim'] = self.secondsInSim
        attribDic['platformFrom'] = self.platformFrom
        attribDic['platformTo'] = self.platformTo
        attribDic['secondsBetweenZChange'] = self.secondsBetweenZChange
        for area in Counts.area_list:
            passes_area = 'false'
            if self.agent_id in area.agents_list:
                passes_area = 'true'
            attribDic['area_'+area.area_id] = passes_area
        return attribDic

class Counts():
    area_list = []
    area_polygon_dic = {}
    time_area_agents_dic = {}
    agentsPerFrameDic = {}

    def __init__(self):
        self.area_list.append(Area(
            area_id='11', xmin=197.16, ymin=115.59, xmax=213.44, ymax=131.75, z=-2.6,
            coord_list=[
                (207.38, 108.62), (213.04, 114.38), (217.39, 110.12), (219.7, 112.47), (222.46, 115.27), (213.65, 124.4),
                (209.54, 120.23), (201.26, 127.82), (198.69, 125.03), (206.88, 117.53), (205.39, 116.01), (197.28, 123.5),
                (194.59, 120.6), (202.66, 113.23), (203.87, 112.05)
            ])
        )
        self.area_list.append(Area(
            area_id='21', xmin=208.23, ymin=100.94, xmax=254.87, ymax=147.81, z=-2.6,
            coord_list=[
                (213.65, 124.4), (209.58, 128.61), (216.55, 135.31), (219.38, 138.02), (222.41, 140.94), (229.32, 133.78),
                (235.03, 139.07), (237.48, 136.34), (238.02, 135.81), (238.74, 134.99), (239.0, 134.74), (241.14, 132.42),
                (243.85, 129.45), (244.4, 128.89), (247.08, 125.95), (248.86, 124.05), (249.56, 123.27), (250.48, 122.28),
                (253.07, 119.47), (244.83, 111.53), (241.97, 108.76), (235.26, 102.91), (222.46, 115.27)
            ])
        )
        self.area_list.append(Area(
            area_id='31', xmin=305.04, ymin=177.52, xmax=350.95, ymax=223.8, z=-5.7,
            coord_list=[
                (309.6, 200.24), (306.25, 204.04), (313.61, 210.4), (316.88, 213.57), (327.44, 222.77), (334.86, 214.43),
                (335.62, 213.55), (337.79, 211.08), (338.29, 210.57), (340.1, 208.49), (340.37, 208.22), (341.17, 207.29),
                (349.95, 197.42), (349.95, 197.42), (339.47, 188.04), (336.6, 185.74), (328.76, 178.69), (324.21, 183.81),
                (321.52, 186.84), (318.73, 190.02), (314.36, 194.86), (312.21, 197.35)
            ])
        )

    def add_frame(self, frame):
        self.time_area_agents_dic[frame] = {}
        for area in self.area_list:
            self.time_area_agents_dic[frame][area.area_id] = []
        self.time_area_agents_dic[frame]['agentsInSim'] = 0

    def add_area_agent_frame(self, frame, area_id, agent_id=None, countAgents = None):
        if frame not in self.time_area_agents_dic:
            self.add_frame(frame)
        if agent_id:
            self.time_area_agents_dic[frame][area_id].append(agent_id)
        elif countAgents:
            self.time_area_agents_dic[frame]['agentsInSim'] = countAgents


class Area():
    def __init__(self, area_id, xmin, ymin, xmax, ymax, z, coord_list):
        self.area_id = area_id
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax
        self.z = z
        self.agents_list = []
        self.coord_list = coord_list


