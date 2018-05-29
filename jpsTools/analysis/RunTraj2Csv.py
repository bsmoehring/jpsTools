import csv

from Agents import Agents, Source
from constants import jps
from coords import Transformation
from TrajectoryOperations import TrajectoryOperations

def main(inputfolder):

    inputTrajectory = inputfolder + 'jps_traj.xml'
    inputIni = inputfolder + 'jps_ini.xml'

    xmin = 799093.3516501468
    ymin = 5828024.700676445

    agents = Agents(inputIni)
    traj = TrajectoryOperations(Transformation(minx=xmin, miny=ymin))
    fps, lastFrame = traj.getAgentsOccurences(inputTrajectory, agents)

    agentsRemoved = cleanAndCalcAgents(fps, lastFrame, agents.agents_sources.sourcesDic)
    print(agentsRemoved, 'agents were removed because they hadnt left the simulation at the last frame')

    StopsManager().assignPlatforms(agents)

    traj.agents2geojson(inputTrajectory, inputfolder+'traj_shape', agents, 8, 1)
    printSourcesToCsv(agents.agents_sources.sourcesDic, inputfolder+'changeTimes.csv')
    printFrameStatisticsToCsv(agents.frame_statistics, inputfolder+'frameStatistics.csv')

    print(inputfolder)
    print(len(agents.agents_sources.sourcesDic), 'agents are considered')
    print(lastFrame, 'last frame of the simulation')

def cleanAndCalcAgents(fps, lastFrame, agents = {}):

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
            agent.frames = agent.lastChangeZFrame-agent.firstChangeZFrame
            agent.secondsBetweenZChange = agent.frames / fps
        else:
            agent.secondsBetweenZChange = 0

    return len(removeIds)

def printSourcesToCsv(sourcesDic, file):
    with open(file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow([jps.Agent_ID, jps.Group_ID, 'firstFrame', 'lastFrame', 'frames', 'seconds',
                         jps.Caption, 'from', 'to', 'firstChangeZFrame', 'lastChangeZFrame', 'secondsBetweenZChange'])

        for source in sourcesDic.values():
            writer.writerow([source.agent_id, source.group_id ,source.firstFrame, source.lastFrame, source.frames, source.secondsInSim,
                             source.caption, source.platformFrom, source.platformTo, source.firstChangeZFrame, source.lastChangeZFrame,
                             source.secondsBetweenZChange])

def printFrameStatisticsToCsv(frame_statistics, file):
    with open(file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow([jps.Frame, 'agentsInSim'])

        for frameID, agents in frame_statistics.agentsPerFrameDic.items():
            writer.writerow([frameID, agents])

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
    input.append('/media/bsmoehring/Data/wichtiges/tuberlin/masterarbeit/runs/0_ipfDemandBasic/')
    input.append('/media/bsmoehring/Data/wichtiges/tuberlin/masterarbeit/runs/1_ipfDemandProg1/')
    input.append('/media/bsmoehring/Data/wichtiges/tuberlin/masterarbeit/runs/2_ipfDemandProg2/')
    for s in input:
        main(s)