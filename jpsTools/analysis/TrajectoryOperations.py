import csv
import xml.etree.ElementTree as ET

from scipy.spatial import Voronoi, voronoi_plot_2d
from shapely import ops, geometry
from shapely.ops import cascaded_union
import pandas as pd
from Agents import Agents, Source, Counts, Area
from constants import jps
from shapely.geometry import *
import fiona
import matplotlib.pyplot as plt

class TrajectoryOperations():

    def __init__(self, transformation, fps, timestampInterval):
        self.transform = transformation
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

        return frameRate, frameId, countFrameAgents

    def agents2shape(self, trajfile, geoJsonFile, agents):

        print(self.__class__.__name__, 'agents2shape', trajfile)

        assert isinstance(agents, Agents)
        properties = {
            jps.Group_ID:'str', jps.Agent_ID:'str', jps.Time:'str', 'firstFrame':'str',
            'lastFrame':'str', 'frames':'str', 'secondsInSim':'float', 'platformFrom':'str', 'platformTo':'str',
            'length':'float'
        }
        for area in Counts.area_list:
            properties['area_'+area.area_id] = 'str'
            properties['minArea'+area.area_id] = 'float'
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
                        trajfile, firstFrames, lastFrames, agents, agent_traj_dic, f, properties
                    )
            self.traj2points(
                trajfile, firstFrames, lastFrames, agents, agent_traj_dic, f, properties
            )

    def traj2points(self, trajfile, firstFrames, lastFrames, agents, agent_traj_dic, f, properties):

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

        for agent_id2, traj in agent_traj_dic.items():
            if len(traj.points) == 0:
                continue
            elif len(traj.points) == 1:
                traj.points.append(traj.points[0])
            linestring = LineString(traj.points)
            linestring_transformed = ops.transform(self.transform.project, linestring)
            agents.agents_sources.sourcesDic[agent_id2].length = linestring_transformed.length
            attribDic = agents.agents_sources.sourcesDic[agent_id2].getAttribDic()
            agent_properties = {your_key: attribDic[your_key] for your_key in properties.keys()}
            f.write({
                'properties': agent_properties,
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

    def frames2Points_Voronois(self, framesAreaDic, trajfile, agents, path):

        print(self.__class__.__name__, 'frames2Points_Voronois', framesAreaDic)
        assert isinstance(agents, Agents)

        file = open(trajfile)

        for event, elem in ET.iterparse(file, ['end']):
            assert isinstance(elem, ET.Element)
            if elem.tag == jps.Frame:
                frameId = elem.attrib[jps.Traj_ID]
                if frameId == '14000':
                #if frameId in framesAreaDic.keys():
                    frame = int(float(frameId))
                    seconds = frame / self.fps

                    area_id = framesAreaDic[frameId]
                    area = None
                    for area1 in agents.counts.area_list:
                        if area1.area_id == area_id:
                            area = area1
                    if area == None:
                        continue
                    area_poly = Polygon(area.coord_list)

                    print(self.__class__.__name__, 'frames2pointlayers', frameId, area_id)
                    points = {}
                    buffers = {}

                    # print(frame)
                    for agentElem in elem.iter(jps.Agent):
                        agent_id = agentElem.attrib[jps.Traj_ID]
                        x = float(agentElem.attrib['x'])
                        y = float(agentElem.attrib['y'])
                        z = float(agentElem.attrib['z'])

                        if z == area.z and x > area.xmin and x < area.xmax and y > area.ymin and y < area.ymax:
                            #counts.add_area_agent_frame(frame=frame, area_id=area.area_id, agent_id=agent_id,
                            #                            countAgents=None)

                            point = (x, y, z)
                            if area_poly.contains(Point(point)):
                                points[agent_id] = point
                        agentElem.clear()
                    print(self.__class__.__name__, 'frames2Points_Voronois', len(points), 'points in area', area_id)

                    #points in area to shape
                    properties = {
                        jps.Group_ID: 'str', jps.Agent_ID: 'str', jps.Time: 'str', 'firstFrame': 'str',
                        'lastFrame': 'str', 'frames': 'str', 'secondsInSim': 'float', 'platformFrom': 'str',
                        'platformTo': 'str'
                    }
                    for area in Counts.area_list:
                        properties['area_' + area.area_id] = 'str'
                        properties['minArea'+area.area_id] = 'float'
                    schema = {
                        'geometry': 'Point',
                        'properties': properties
                    }
                    #write points
                    with fiona.open(path+'points_area_'+area_id, 'w', 'ESRI Shapefile', schema) as f:

                        for agent_id, point in points.items():
                            lat, lon = self.transform.XY2WGS(
                                point[0],
                                point[1]
                            )
                            f.write({
                                'properties': agents.agents_sources.sourcesDic[agent_id].getAttribDic(),
                                'geometry': mapping(Point(lon, lat, point[2]))
                            })

                    #union of all buffered points to shape
                    schema = {
                        'geometry': 'Polygon',
                        'properties': {jps.Agent_ID: 'str'}
                    }
                    for agent_id, point in points.items():
                        # raduis around agent
                        bufferPoly = Point(point).buffer(1.02)
                        # check if radius intersects room:
                        bufferPoly = bufferPoly.intersection(Polygon(area_poly))
                        buffers[agent_id] = bufferPoly
                    buffers = cascaded_union(buffers.values())
                    #write buffers
                    # with fiona.open(path + 'points_area_' + area_id + '_buffer_1m', 'w', 'ESRI Shapefile',
                    #                 schema) as f:
                    #     for agent_id, point in points.items():
                    #         coords = []
                    #         for coord in bufferPoly.exterior.coords:
                    #             lat, lon = self.transform.XY2WGS(coord[0], coord[1])
                    #             coords.append((lon, lat, point[2]))
                    #         f.write({
                    #             'properties': {jps.Agent_ID: agent_id},
                    #             'geometry': mapping(Polygon(coords))
                    #         })

                    # Voronoi
                    points_for_vor = [[-1000, -1000], [-1000, 1000], [1000, -1000], [1000, 1000]]
                    for agent_id, point in points.items():
                        points_for_vor.append([point[0], point[1]])
                    vor = Voronoi(points_for_vor)
                    print(vor)
                    lines = [
                        LineString(vor.vertices[line])
                        for line in vor.ridge_vertices
                        if -1 not in line
                        ]

                    # write voronois
                    schema = {
                        'geometry': 'Polygon',
                        'properties': {jps.Agent_ID: 'str', 'sqm':'float'}
                    }
                    with fiona.open(path + 'voronoi' + area_id + 'frame' + frameId, 'w', 'ESRI Shapefile', schema) as f:
                        for poly in ops.polygonize(lines):
                            #search agent_id by intersecting point
                            properties = {jps.Agent_ID: ''}
                            for agent_id, point in points.items():
                                 if poly.contains(Point(point)):
                                     properties[jps.Agent_ID] = agent_id
                                     break
                            poly = poly.intersection(buffers)
                            print(poly.area)
                            properties['sqm'] = poly.area
                            coords = []
                            for coord in poly.exterior.coords:
                                lat, lon = self.transform.XY2WGS(coord[0], coord[1])
                                coords.append((lon, lat, area.z))
                            poly = Polygon(coords)
                            f.write({
                                'properties': properties,
                                'geometry': mapping(poly)
                            })



                elem.clear()
        file.close()

    def area_statistics(self, trajfile, agents, path):

        print(self.__class__.__name__, 'area_statistics', trajfile)

        assert isinstance(agents, Agents)

        file = open(trajfile)

        with open(path+'areaLoS.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            columns = ['frame']
            for area in agents.counts.area_list:
                columns.append(area.area_id+'_numb')
                columns.append(area.area_id+'_minA')
                columns.append(area.area_id+'_maxA')
                columns.append(area.area_id+'_avgA')
                columns.append(area.area_id+'_n_A')
                columns.append(area.area_id+'_n_B')
                columns.append(area.area_id+'_n_C')
                columns.append(area.area_id+'_n_D')
                columns.append(area.area_id+'_n_E')
                columns.append(area.area_id+'_n_F')

                area.area_poly = Polygon(area.coord_list)
                area.frame_agent_points = {}
            writer.writerow(columns)

            for event, elem in ET.iterparse(file, ['end']):
                assert isinstance(elem, ET.Element)

                if elem.tag == jps.Frame:
                    frameId = elem.attrib[jps.Traj_ID]
                    frame = int(float(frameId))
                    seconds = frame / self.fps

                    if frame % self.frameDivisor == 0:
                        print(frame)
                        # check if any agent is in one of the areas
                        for agentElem in elem.iter(jps.Agent):

                            agent_id = agentElem.attrib[jps.Traj_ID]
                            handle = False
                            x = float(agentElem.attrib['x'])
                            y = float(agentElem.attrib['y'])
                            z = float(agentElem.attrib['z'])

                            for area in agents.counts.area_list:

                                if z == area.z and x > area.xmin and x < area.xmax and y > area.ymin and y < area.ymax:
                                    p = Point(x, y)
                                    if area.area_poly.contains(p):
                                        area.frame_agent_points[agent_id] = p
                            agentElem.clear()
                        elem.clear()

                        row = [frameId]
                        for area in agents.counts.area_list:
                            buffers = []
                            for p in area.frame_agent_points.values():
                                buffers.append(p.buffer(1.02))
                            buffers = cascaded_union(buffers)
                            buffers = buffers.intersection(area.area_poly)
                            # Voronoi
                            points_for_vor = [[-1000, -1000], [-1000, 1000], [1000, -1000], [1000, 1000]]
                            for agent_id, point in area.frame_agent_points.items():
                                points_for_vor.append([point.x, point.y])
                            vor = Voronoi(points_for_vor)
                            lines = [
                                LineString(vor.vertices[line])
                                for line in vor.ridge_vertices
                                if -1 not in line
                                ]
                            voronoi_area_list = []
                            for poly in ops.polygonize(lines):
                                # search agent_id by intersecting point
                                poly = poly.intersection(buffers)
                                #assignagent
                                for agent_id, p in area.frame_agent_points.items():
                                    if poly.contains(p):
                                        try:
                                            agents.agents_sources.sourcesDic[agent_id].addArea(area.area_id, round(poly.area, 2))
                                        except KeyError:
                                            pass
                                        break
                                voronoi_area_list.append(poly.area)
                                #x, y = poly.exterior.xy
                                #plt.plot(x, y, color='#6699cc', alpha=0.7, linewidth=1, solid_capstyle='round', zorder=2)
                            if voronoi_area_list:
                                row.append(len(voronoi_area_list))
                                row.append(round(min(voronoi_area_list),2))
                                row.append(round(max(voronoi_area_list),2))
                                row.append(round(sum(voronoi_area_list) / float(len(voronoi_area_list)),2))
                                row.append(sum(i >= 3.24 for i in voronoi_area_list))
                                row.append(sum(i >= 2.32 and i < 3.24 for i in voronoi_area_list))
                                row.append(sum(i >= 1.39 and i < 2.32 for i in voronoi_area_list))
                                row.append(sum(i >= 0.93 and i < 1.39 for i in voronoi_area_list))
                                row.append(sum(i >= 0.46 and i < 0.93 for i in voronoi_area_list))
                                row.append(sum(i < 0.46 for i in voronoi_area_list))
                            else:
                                row.extend([0, 'NaN', 'NaN', 'NaN', 0, 0, 0, 0, 0, 0])

                                #x, y = area.area_poly.exterior.xy
                                #plt.plot(x, y, color='#6699cc', alpha=0.7,
                                #         linewidth=3, solid_capstyle='round', zorder=2)
                                #plt.show()
                                #plt.close()

                            print(trajfile, seconds, area.area_id, len(area.frame_agent_points.keys()))
                            area.frame_agent_points.clear()

                        writer.writerow(row)

                    elem.clear()

            file.close()


class AgentTraj:

    def __init__(self, agent_id):

        self.agent_id = agent_id
        self.points = []

    def addPoint(self, lat, lon, z, seconds):
        self.points.append((lon, lat, z))
