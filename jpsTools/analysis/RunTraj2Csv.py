import csv

from Agents import Agents, Source, Counts, Area
from constants import jps
from coords import Transformation
from TrajectoryOperations import TrajectoryOperations

def main(input):

    print('###')
    print(input[0])
    inputfolder = input[0]

    inputTrajectory = inputfolder + 'jps_traj.xml'
    inputIni = inputfolder + 'jps_ini.xml'

    xmin = 799093.3516501468
    ymin = 5828024.700676445

    timestampInterval = 1

    counts = Counts()

    agents = Agents(inputIni)
    traj = TrajectoryOperations(Transformation(minx=xmin, miny=ymin), timestampInterval=timestampInterval, fps=agents.fps)
    fps, lastFrame = traj.getAgentsOccurences(trajfile=inputTrajectory, agents=agents)
    agentsRemoved = cleanAndCalcAgents(fps, lastFrame, agents.agents_sources.sourcesDic)
    print(agentsRemoved, 'agents were removed because they hadnt left the simulation at the last frame')
    StopsManager().assignPlatforms(agents)

    traj.assign_areas(
        trajfile=inputTrajectory, agents=agents, counts=agents.counts
    )

    #traj.frames2Points_Voronois(agents=agents, path=inputfolder, trajfile=inputTrajectory, framesAreaDic=input[1])

    traj.agents2shape(inputTrajectory, inputfolder + 'traj_shape', agents)
    printSourcesToCsv(agents, inputfolder+'changeTimes.csv')
    printFrameStatisticsToCsv(agents.counts, inputfolder+'frameStatistics.csv')

    print(inputfolder)
    print(len(agents.agents_sources.sourcesDic), 'agents are considered')
    #print(lastFrame, 'last frame of the simulation')

    agents.clear()

def cleanAndCalcAgents(fps, lastFrame, agents = {}):
    print('cleanAndCalcAgents')

    # remove agents that haven't appeared or didn't leave the simulation yet
    removeIds = []
    for agent_id, agent in agents.items():
        if agent.firstFrame == None or agent.lastFrame == int(float(lastFrame)):
            removeIds.append(agent_id)
    for agent_id in removeIds:
       del agents[agent_id]

    # calculate time in simulation
    for agent_id, agent in agents.items():
        assert isinstance(agent, Source)
        agent.frames = agent.lastFrame-agent.firstFrame
        agent.secondsInSim = agent.frames / fps
        if agent.lastChangeZFrame != None and agent.firstChangeZFrame != None and agent.lastChangeZFrame != agent.firstChangeZFrame:
            agent.zframes = agent.lastChangeZFrame-agent.firstChangeZFrame
            agent.secondsBetweenZChange = agent.zframes / fps
        else:
            agent.secondsBetweenZChange = None
            agent.zframes = None

    return len(removeIds)

def printSourcesToCsv(agents, file):
    print('printSourcesToCsv', file)
    with open(file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        columns = [jps.Group_ID, jps.Agent_ID, jps.Time, 'firstFrame',
                'lastFrame', 'frames', 'secondsInSim', 'platformFrom', 'platformTo']
        for area in agents.counts.area_list:
            columns.append('area_'+area.area_id)
        writer.writerow(columns)
        for source in agents.agents_sources.sourcesDic.values():
            attribDic = source.getAttribDic()
            row = []
            for column in columns:
                row.append(attribDic[column])
            writer.writerow(row)

def printFrameStatisticsToCsv(counts, file):

    print('printFrameStatisticsToCsv', file)

    assert isinstance(counts, Counts)
    with open(file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        columns = [jps.Frame, 'agentsInSim']
        for area in counts.area_list:
            columns.append(area.area_id)
        writer.writerow(columns)

        for frameId, area_agents_dic in sorted(counts.time_area_agents_dic.items()):
            row = []
            for column in columns:
                if column == jps.Frame:
                    row.append(frameId)
                elif column == 'agentsInSim':
                    row.append(area_agents_dic[column])
                else:
                    row.append(len(area_agents_dic[column]))
            writer.writerow(row)

class StopsManager():

    goalsPlatformDic = {}
    roomsPlatformDic = {}

    def __init__(self):
        self.roomsPlatformDic['2']      = 'Regio'
        self.roomsPlatformDic['1']      = 'S'
        self.roomsPlatformDic['53']     = 'U2'
        self.roomsPlatformDic['39']     = 'U5'
        self.roomsPlatformDic['32']     = 'U8'
        self.roomsPlatformDic['2914']   = 'Tram U'
        self.roomsPlatformDic['291']    = 'Dircksenstr.'
        self.roomsPlatformDic['17']     = 'Gontardstr.'

        self.goalsPlatformDic['026']    = 'Regio'
        self.goalsPlatformDic['0212']   = 'Regio'
        self.goalsPlatformDic['025']    = 'Regio'
        self.goalsPlatformDic['0211']   = 'Regio'
        self.goalsPlatformDic['015']    = 'S'
        self.goalsPlatformDic['0111']   = 'S'
        self.goalsPlatformDic['016']    = 'S'
        self.goalsPlatformDic['0112']   = 'S'
        self.goalsPlatformDic['532']    = 'U2'
        self.goalsPlatformDic['535']    = 'U2'
        self.goalsPlatformDic['533']    = 'U2'
        self.goalsPlatformDic['536']    = 'U2'
        self.goalsPlatformDic['403']    = 'U5'
        self.goalsPlatformDic['402']    = 'U5'
        self.goalsPlatformDic['322']    = 'U8'
        self.goalsPlatformDic['325']    = 'U8'
        self.goalsPlatformDic['323']    = 'U8'
        self.goalsPlatformDic['326']    = 'U8'
        self.goalsPlatformDic['2914']   = 'Tram U'
        self.goalsPlatformDic['291']    = 'Dircksenstr.'
        self.goalsPlatformDic['173']    = 'Gontardstr.'

    def assignPlatforms(self, agents):
        '''
        assign caption and platforms according to group room, subroom and goal
        :param agents:
        :return:
        '''
        assert isinstance(agents, Agents)
        for agent_id, source in agents.agents_sources.sourcesDic.items():
            group = agents.agents_distribution.groupsDic[source.group_id]
            source.caption = group.caption
            if group.caption == 'change':
                self.assignPlatformFrom(source, group)
                self.assignPlatfomTo(source, group)
            elif group.caption == 'enter':
                self.assignPlatfomTo(source, group)
            elif group.caption == 'leave':
                self.assignPlatformFrom(source, group)

    def assignPlatfomTo(self, source, group):
        source.platformTo = self.goalsPlatformDic[group.goal_id]

    def assignPlatformFrom(self, source, group):
        if group.room_id in self.roomsPlatformDic:
            source.platformFrom = self.roomsPlatformDic[group.room_id]
        else:
            source.platformFrom = self.roomsPlatformDic[group.room_id+group.subroom_id]


if __name__ == "__main__":
    input = []
    #input.append(('/media/bsmoehring/Data/wichtiges/tuberlin/masterarbeit/runs/0_ipfDemandBasic/', {'10344': '11', '10544': '21', '6784': '31'}))
    #input.append(('/media/bsmoehring/Data/wichtiges/tuberlin/masterarbeit/runs/1_ipfDemandProg1/', {'12824': '11', '12544': '21', '2904': '31'}))
    input.append(('/media/bsmoehring/Data/wichtiges/tuberlin/masterarbeit/runs/2_ipfDemandProg2/', {}))
    #input.append(('/media/bsmoehring/Data/wichtiges/tuberlin/masterarbeit/tests/report/smalltraj/', {}))

    for s in input:
        main(s)


