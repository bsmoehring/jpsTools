import xml.etree.ElementTree as ET
from constants import jps

class Agents():

    def __init__(self, inifile):

        self.agents_distribution = Agents_Distribution()
        self.agents_sources = Agents_Sources()
        self.frame_statistics = Frame_Statistics()

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

        file.close()

        print('groups: ', len(self.agents_distribution.groupsDic))
        print('agents: ', len(self.agents_sources.sourcesDic))

class Frame_Statistics:

    agentsPerFrameDic = {}

class Agents_Distribution:

    groupsDic = {}

    def addGroup(self, group):
        self.groupsDic[group.group_id] = group

class Agents_Sources:

    sourcesDic = {}

    def addSource(self, source):
        self.sourcesDic[source.agent_id] = source

    def addOccurence(self, agent_id, frame):

        source = self.sourcesDic[agent_id]
        if source.firstFrame == None:
            source.firstFrame = frame
        if source.lastFrame < frame:
            source.lastFrame = frame

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
        self.lastFrame = 0
        self.frames = None
        self.secondsInSim = None
        self.platformFrom = None
        self.platformTo = None

    def getGroup(self):
        '''
        get Group of this Source
        :return:
        '''

        return Agents_Distribution().groupsDic[self.group_id]