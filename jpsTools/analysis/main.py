import csv

from agents import Agents
from constants import jps
from trajectory import Trajectory

def main():

    inputfolder = '/media/bsmoehring/Data/wichtiges/tuberlin/masterarbeit/runs/1_ipfDemandProg1/'
    inputTrajectory = inputfolder + 'jps_traj.xml'
    inputIni = inputfolder + 'jps_ini.xml'

    outputCsv = inputfolder + 'changeTimes.csv'


    # xMin = 175.0
    # yMin = 122.5
    # xMax = 180.2
    # yMax = 128.0
    # z = -1.3

    agents = Agents(inputIni)
    fps, lastFrame = Trajectory().getAgentsOccurences(inputTrajectory, agents)

    cleanAndCalcAgents(fps, lastFrame, agents.agents_sources.sourcesDic)

    StopsManager().assignPlatforms(agents)

    printToCsv(agents.agents_sources.sourcesDic, outputCsv)

    print(len(agents.agents_sources.sourcesDic))
    print(lastFrame)

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
        agent.frames = agent.lastFrame-agent.firstFrame
        agent.secondsInSim = agent.frames / fps

def printToCsv(sourcesDic, file):
    with open(file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow([jps.Agent_ID, 'firstFrame', 'lastFrame', 'frames', 'seconds',
                         jps.Caption, 'from', 'to'])

        for agent in sourcesDic.values():
            writer.writerow([agent.agent_id, agent.firstFrame, agent.lastFrame, agent.frames, agent.secondsInSim,
                             agent.caption, agent.platformFrom, agent.platformTo])

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
    main()