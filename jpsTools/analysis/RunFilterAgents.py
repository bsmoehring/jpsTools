import csv

from Agents import Agents, Source, Area, Counts
from constants import jps
from coords import Transformation
from TrajectoryOperations import TrajectoryOperations

def main(inputfolder):

    inputTrajectory = inputfolder + 'jps_traj.xml'
    inputIni = inputfolder + 'jps_ini.xml'

    xmin = 799093.3516501468
    ymin = 5828024.700676445

    agents = Agents(inputIni)

    traj = TrajectoryOperations(transform=Transformation(minx=xmin, miny=ymin), fps=agents.fps, timestampInterval=1)
    traj.assign_areas(trajfile=inputTrajectory, agents=agents, counts=agents.counts)
    printFrameStatisticsToCsv(agents.counts, inputfolder+'frame_area_agents.csv')
    traj.filter_traj_by_areas(trajfile=inputTrajectory, counts=agents.counts)

def printFrameStatisticsToCsv(counts, file):

    print('printFrameStatisticsToCsv', file)

    assert isinstance(counts, Counts)
    with open(file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        columns = [jps.Frame]
        for area in counts.area_list:
            columns.append(area.area_id)
        writer.writerow(columns)

        for frameId, area_agents_dic in sorted(counts.time_area_agents_dic.items()):
            row = []
            for column in columns:
                if column == jps.Frame:
                    row.append(frameId)
                else:
                    row.append(len(area_agents_dic[column]))
            writer.writerow(row)

if __name__ == "__main__":
    input = []
    # input.append('/media/bsmoehring/Data/wichtiges/tuberlin/masterarbeit/runs/0_ipfDemandBasic/')
    # input.append('/media/bsmoehring/Data/wichtiges/tuberlin/masterarbeit/runs/1_ipfDemandProg1/')
    #input.append('/media/bsmoehring/Data/wichtiges/tuberlin/masterarbeit/runs/2_ipfDemandProg2/')
    input.append('/media/bsmoehring/Data/wichtiges/tuberlin/masterarbeit/tests/report/smalltraj/')

    counts = Counts()
    counts.add_area(Area('11', 197.16, 115.59, 213.44, 131.75, -2.6))
    #counts.add_area(Area('21', 208.23, 100.94, 254.87, 147.81, -2.6))
    #counts.add_area(Area('31', 305.04, 177.52, 350.95, 223.8, -5.7))

    for s in input:
        main(s)

