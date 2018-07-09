import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import itertools
import math
#from Agents import Agents, Source
#from constants import jps

def plotTimeVariationForGroup(outputFolder, column, platformFrom = [], platformTo = [],  input_list = []):

    # assert isinstance(agents, Agents)
    #
    # changesList = []
    #
    # for agentId, source in agents.agents_sources.sourcesDic.items():
    #     assert(source, Source)
    #     if source.platformFrom == platformFrom and source.platformTo == platformTo:
    #         changesList.append(source)
    print(platformFrom, platformTo)
    maximum_list = []

    for inputDic in input_list:


        file = inputDic['file']+'changeTimes.csv'
        label = inputDic['label']
        color = inputDic['color']
        opacity = inputDic['opacity']

        changes = pd.read_csv(file, sep=';', converters={column:float, 'time':int})
        changes = changes.dropna(subset=[column])
        selectedChanges = changes.loc[
            (changes['time'] >= 300)
#            & ((changes['area_11'] == True) | (changes['area_21'] == True) | (changes['area_31'] == True))
        ]
        if platformFrom:
            selectedChanges = selectedChanges.loc[
                (changes['platformFrom'].isin(platformFrom)) | (changes['platformTo'].isin(platformFrom))
            ]
        if platformTo:
            selectedChanges = selectedChanges.loc[
                (changes['platformTo'].isin(platformTo)) | (changes['platformFrom'].isin(platformTo))
            ]
        plotAverage(plt, column, selectedChanges, color, 0)

    #legend = ['Basis\nn = '+str(len(selectedChanges.index)), 'Prognose\nn = '+str(len(selectedChangesProg.index))]
    #counts, bins, bars = plt.hist([selectedChanges['seconds'], selectedChangesProg['seconds']], bins=np.arange(0, 360, 20), color=['blue', 'red'], alpha=0.5)

        maximum = plot(column, selectedChanges, color, label, opacity)
        maximum_list.append(maximum)

    if platformFrom:
        platformFrom = '_'.join(platformFrom)
    else:
        platformFrom = 'None'
    if platformTo:
        platformTo = '_'.join(platformFrom)
    else:
        platformTo = 'None'

    plt.legend()
    plt.xlabel("Zeit in Sekunden")
    plt.ylabel("Häufigkeit")
    maximum = int(max(maximum_list))
    print(maximum)
    plt.yticks(np.arange(0, maximum+1, roundup(maximum/5)))
    #plt.yticks(np.arange(0, 400, 50))
    plt.xticks(np.arange(0, 360, 50))
    plt.title(column)
    plt.show()
    plt.draw()

    plt.savefig(outputFolder + platformFrom + '_' + platformTo + '_' + column + '.png')
    plt.close()

def plot(column, selectedChanges, color, label, opacity):

    countBase, _, _ = plt.hist(
        selectedChanges[column], bins=np.arange(0, 360, 10), histtype='stepfilled', color=color, alpha=opacity,
        label=label+'\nn = '+str(len(selectedChanges.index))+'\n\u2205 = '+str(int(round(selectedChanges[column].mean(),0)))
    )
    return countBase.max()


def roundup(x):
    return int(math.ceil(x / 10.0)) * 10


def plotAverage(plt, column, changes, color, offset):
    mean = changes[column].mean()
    plt.axvline(x=mean, color=color, linestyle='dashed')
    #print(mean)
    # plt.text(mean+offset, plt.gca().get_ylim()[1]/2, '\u2205 \n' + str(int(round(mean, 0))),
    #          horizontalalignment='center',
    #          verticalalignment='center',
    #          color=color,
    #          bbox=dict(facecolor='white', alpha=0.9))

def plotFrameAreaAgents(output, area, fps, group_seconds, input_list = []):
    for inputDic in input_list:

        file = inputDic['file']+'frameStatistics.csv'
        label = inputDic['label']
        color = inputDic['color']
        offset = inputDic['offset']
        frames = pd.read_csv(file, sep=';', converters={0:int, 1:int, 2:int, 3:int, 4:int, 5:int})
        selectedFrames = frames.loc[
            (frames['frame']%(fps) == 0)
        ]
        selectedFramesMeans = selectedFrames.groupby(
            pd.cut(selectedFrames['frame'], np.arange(0, 14000+(group_seconds*fps), group_seconds*fps))
        ).mean()
        plt.plot(selectedFramesMeans['frame'] / fps, selectedFramesMeans[str(area)], color=color, label=label,
                 alpha=0.9, linewidth=0.7)

        #print(selectedFramesMeans)

        selectedFramesMeans = selectedFrames.groupby(
            pd.cut(selectedFrames['frame'], np.arange(0, 14000 + (5 * fps), 5 * fps))
        ).mean()
        maxagents_frame = plotMax(plt, selectedFramesMeans, area, color, offset, fps)
        inputDic['maxagents_frame_area_'+str(area)] = str(int(maxagents_frame))


    leg = plt.legend(loc='center left', fancybox=True, bbox_to_anchor=(0.0, 0.2))
    leg.get_frame().set_alpha(1.0)
    plt.title('Detail '+str(area)[0])
    plt.xlabel('Zeit in Sekunden')
    plt.xticks(np.arange(0, 1801, 300))
    plt.ylabel('Anzahl Personen')
    # #plt.show()
    plt.draw()
    plt.savefig(output)
    plt.close()

def plotMax(plt, df, area, color, offset, fps):

    maxY = int(df[str(area)].max())
    maxY_X = df.loc[df[str(area)].idxmax()]['frame']
    ylim = plt.axes().get_ylim()[1]
    plt.axvline(x=maxY_X / fps, ymax=maxY/ylim*ylim, color=color, linestyle='dashed')
    plt.text(x=maxY_X / fps, y=0,
             s='Sek: \n'+str(int(round(maxY_X/fps, 0))),
             horizontalalignment='center',
             verticalalignment='center',
             color=color,
             bbox=dict(facecolor='white', alpha=1.0)
    )
    plt.text(x=maxY_X/fps, y= 0.9*(maxY/ylim*ylim),
             s='Max: '+str(maxY),
             horizontalalignment='center',
             verticalalignment='center',
             color=color,
             bbox=dict(facecolor='white', alpha=1.0)
    )
    mean = int(round(df[str(area)].mean(),0))
    plt.axhline(y=1.0*(mean/ylim*ylim) , color=color, linestyle='dashed')
    plt.text(x=0., y= 1.0*(mean/ylim*ylim)+offset,
             s='\u2205: '+str(mean),
             horizontalalignment='center',
             verticalalignment='center',
             color=color,
             bbox=dict(facecolor='white', alpha=1.0)
    )
    return maxY_X

def runAggregateStatistics(input_csv, label, arealist, area_quality_dic):
    changes = pd.read_csv(
        input_csv, sep=';',
        converters={
            'secondsInSim': float, 'time': int,
            'minArea11':float, 'minArea21':float, 'minArea31':float
        }
    )
    mean = round(changes['secondsInSim'].mean(), 2)
    selected_changes = changes.loc[
        (changes['time'] >= 300)
        & ((changes['area_11'] == True) | (changes['area_21'] == True) | (changes['area_31'] == True))
    ]
    selected_changes_time_mean = round(selected_changes['secondsInSim'].mean(), 2)
    print(
        label,
        'all:', changes.shape[0], 'mean:', mean, 'deviation', round(changes['secondsInSim'].std(),2),
        'areas', selected_changes.shape[0], 'mean:', selected_changes_time_mean, 'var', round(selected_changes['secondsInSim'].std(),2)
    )

    for area in arealist:
        area_column = 'area_'+str(area)
        minArea_column = 'minArea'+str(area)
        selected_changes = changes.loc[
            (changes['time'] >= 300)
            & (changes[area_column]==True)
        ]
        area_mean = round(selected_changes[minArea_column].mean(), 2)
        area_quality_dic[area]['N'].append(selected_changes.shape[0])
        area_quality_dic[area]['A'].append(selected_changes.loc[(selected_changes[minArea_column] >= 3.24)].shape[0])
        area_quality_dic[area]['B'].append(selected_changes.loc[
            (selected_changes[minArea_column] < 3.24) & (selected_changes[minArea_column] >= 2.32)].shape[0])
        area_quality_dic[area]['C'].append(selected_changes.loc[
            (selected_changes[minArea_column] < 2.32) & (selected_changes[minArea_column] >= 1.39)].shape[0])
        area_quality_dic[area]['D'].append(selected_changes.loc[
            (selected_changes[minArea_column] < 1.39) & (selected_changes[minArea_column] >= 0.93)].shape[0])
        area_quality_dic[area]['E'].append(selected_changes.loc[
            (selected_changes[minArea_column] < 0.93) & (selected_changes[minArea_column] >= 0.46)].shape[0])
        area_quality_dic[area]['F'].append(selected_changes.loc[(selected_changes[minArea_column] < 0.46)].shape[0])

        print(
            label, area_column,
            'N =', selected_changes.shape[0],
            'areaMean', area_mean,
            'A', area_quality_dic[area]['A'][-1],
            'B', area_quality_dic[area]['B'][-1],
            'C', area_quality_dic[area]['C'][-1],
            'D', area_quality_dic[area]['D'][-1],
            'E', area_quality_dic[area]['E'][-1],
            'F', area_quality_dic[area]['F'][-1]
        )
def plotAreaDensity(input_list, areas, fps, path):
    f, ax = plt.subplots(1, 3, sharey=True, sharex=True, figsize=(10, 3))
    f.subplots_adjust(bottom=0.2)  # make room for the legend
    plt.gca().set_ylim(0.4, 3.25)
    plt.yticks(np.arange(0.5, 3.5, 0.5))
    plt.xticks(np.arange(300, 1801, 500))
    lines = []
    labels=[]
    #plt.rcParams.update({'font.size': 14})
    outputfile = path + 'densityinarea.png'

    def create_subplot(column, axis, area):
        axis.set_title('Detail '+str(area)[0])
        axis.yaxis.grid(color='lightgrey', linewidth=0.5)
        axis.tick_params(pad=10)
        for input in input_list:
            color = input['color']
            label = input['label']
            offset = input['offset']
            file = input['file'] + 'areaLoS.csv'
            converters = {'frame': int}
            converters[str(area) + '_numb'] = int
            converters[str(area) + '_minA'] = float
            converters[str(area) + '_maxA'] = float
            converters[str(area) + '_avgA'] = float
            frames = pd.read_csv(file, sep=';', converters=converters)
            selectedFrames = frames.loc[
                ((frames['frame'] % (fps) == 0)) & (frames['frame'] > 300 * fps)
                ]
            selectedFramesMeans = selectedFrames.groupby(
                pd.cut(selectedFrames['frame'], np.arange(0, 14000 + (20 * fps), 20 * fps))
            ).mean()
            lines.append(axis.plot(
                selectedFramesMeans['frame'] / fps, selectedFramesMeans[column],
                color=color, label=label, alpha=0.9, linewidth=0.7
            ))
            ylim = plt.gca().get_ylim()[1]
            mean = selectedFrames[column].mean()
            y = 1.0 * (mean / ylim * ylim) - offset / 7
            # plt.axhline(y=mean, color=color, linewidth=1.5)
            if label == 'Basis':
                axis.text(
                    x=270, y=y+0.35,
                    s='avg:',
                    horizontalalignment='center',
                    verticalalignment='center',
                    color='black',
                    bbox=dict(facecolor='white', alpha=1.0)
                )
            axis.text(
                x=270, y=y,
                s= str(round(mean, 2)),
                horizontalalignment='center',
                verticalalignment='center',
                color=color,
                bbox=dict(facecolor='white', alpha=1.0)
            )
            minY = selectedFrames[column].min()
            minY_X = selectedFrames.loc[selectedFrames[column].idxmin()]['frame']
            axis.axvline(x=minY_X / fps, color=color, linewidth=1.5, ymax=(minY / ylim ))
            if area == 31 and label == 'Basis': y=0.5
            else: y = 0.1
            axis.text(
                x=minY_X/fps, y=y,
                s=str(int(round(minY_X / fps, 0))),
                horizontalalignment='center',
                verticalalignment='center',
                color=color,
                bbox=dict(facecolor='white', alpha=1.0)
            )
            y = (minY / ylim * ylim)
            if area == 31 and label == 'Basis': y-=offset/20
            if y < 0.7: y = 0.7
            axis.text(x=minY_X / fps, y=y,
                     s=str(minY),
                     horizontalalignment='center',
                     verticalalignment='center',
                     color=color,
                     bbox=dict(facecolor='white', alpha=1.0)
                     )
            # print(area, label, minY, int(minY_X))

    for area in areas:
        create_subplot(column = str(area)+'_avgA', axis=ax[areas.index(area)], area=area)

    ax[0].set_ylabel('$m^2$ / Person')  # add left y label
    ax[0].set_ybound(0, 3.25)  # add buffer at the top of the bars
    ax[0].set_xlabel('Zeit in Sekunden')
    ax[2].set_xlabel('Zeit in Sekunden')
    handles, labels = ax[0].get_legend_handles_labels()
    leg = f.legend(handles, labels, loc='lower center', ncol=3)
    for legobj in leg.legendHandles:
        legobj.set_linewidth(2.0)
    f.tight_layout()
    plt.savefig(outputfile)
    plt.show()
    plt.close()

def plot_minAreas(areas, input_list, qualities, path):
    area_quality_dic = {}
    for area in areas:
        area_quality_dic[area] = {'N':[]}
        for quality in qualities:
            area_quality_dic[area][quality] = []
    for input in input_list:
        runAggregateStatistics(input['file'] + 'changeTimes.csv', input['label'], areas, area_quality_dic)

    colors = ['#fff5f0', '#fcccb7', '#fb8e6e', '#f34d37', '#c4161b', '#67000d']
    model_names = ['Basis', 'Prog 1', 'Prog 2']
    ind = np.arange(3)
    f, ax = plt.subplots(1, 3, sharey=True, sharex=True, figsize=(5, 4))
    plt.yticks(np.arange(0, 4500, 500))
    #plt.xticks(ind, model_names)
    p = []  # list of bar properties
    m = [] # list if model properties

    def create_subplot(matrix, colors, axis, title, n, model_names):
        bar_renderers = []
        model_renderers = []
        ind = np.arange(matrix.shape[1])
        bottoms = np.cumsum(np.vstack((np.zeros(matrix.shape[1]), matrix)), axis=0)[:-1]
        for i in ind:
            print(i, input_list[i]['color'])
            r = axis.bar(model_names[i], n[i], width=0.8, fill=False
                     , linewidth=3, edgecolor=input_list[i]['color']
                     )
            model_renderers.append(r)
        for i, row in enumerate(matrix):
            r = axis.bar(ind, row, width=0.7, color=colors[i], bottom=bottoms[i])
            bar_renderers.append(r)
        axis.set_title(title)
        axis.get_xaxis().set_visible(False)
        #plt.sca(axis)
        #plt.xticks(rotation=45)
        return bar_renderers, model_renderers

    for area in areas:
        values = []
        n = []
        for quality in qualities:
            values.append(area_quality_dic[area][quality])
        n.extend(area_quality_dic[area]['N'])
        bar_renderers, model_renderers = create_subplot(np.array(values), colors, ax[areas.index(area)], 'Detail '+str(area)[0], n, model_names)
        p.extend(bar_renderers)
        m.extend(model_renderers)

    ax[0].set_ylabel('Anzahl Agenten')  # add left y label
    ax[0].set_ybound(0, 4400)  # add buffer at the top of the bars
    f.legend(((x[0] for x in m)),  # bar properties
             ('Basis', 'Prognose 1', 'Prognose 2'),
             bbox_to_anchor=(0.55, 0.065),
             loc='lower center',
             ncol=3)
    f.legend(((x[0] for x in p)),  # bar properties
             (qualities),
             bbox_to_anchor=(0.55, 0),
             loc='lower center',
             ncol=6)
    f.tight_layout()
    f.subplots_adjust(bottom=0.15)  # make room for the legend
    plt.savefig(path+'minAreas.png')
    plt.show()
    plt.close()


def nameEarlyAgents(input_list, platformFrom, platformTo):

    for inputDic in input_list:

        file = inputDic['file']+'changeTimes.csv'
        label = inputDic['label']

        changes = pd.read_csv(file, sep=';', converters={'secondsInSim':float, 'time':int})
        selectedChanges = changes.loc[
            ((changes['platformFrom'] == platformFrom) & (changes['platformTo'] == platformTo))
            & (changes['secondsInSim'] < 20)
        ]
        print(selectedChanges['agent_id'])
        print(label, selectedChanges.shape[0], 'were early and removed:(')


if __name__ == "__main__":

    platforms=[
        'S', 'Regio', 'U2', 'U5', 'U8'
#        , 'Gontardstr.', 'Dircksenstr.', 'Tram U'
    ]
    areas = [11, 21, 31]
    qualities = ['A','B','C','D','E','F']

    input= '/media/bsmoehring/Data/wichtiges/tuberlin/masterarbeit/runs/'
    inputBasis = {'file':input + '0_ipfDemandBasic/', 'label':'Basis', 'color':'grey', 'opacity':0.4, 'offset':-2}
    inputProg1 = {'file':input + '1_ipfDemandProg1/', 'label':'Prog 1', 'color':'orange', 'opacity':0.25, 'offset':0}
    inputProg2 = {'file':input + '2_ipfDemandProg2/', 'label':'Prog 2', 'color':'darkred', 'opacity':0.3, 'offset':+2}
    input_list = [inputBasis, inputProg1, inputProg2]

    #plotTimeVariationForGroup(
    #        outputFolder=input+'analysis/', column='secondsInSim',
    #        platformFrom='S', platformTo='U2',
    #        input_list=input_list)
    plotTimeVariationForGroup(
            outputFolder=input+'analysis/', column='secondsInSim',
            platformFrom=[], platformTo=[],
            input_list=input_list
    )

    for platformFrom, platformTo in itertools.combinations(platforms, 2):
        if platformFrom == 'S' and platformTo == 'Regio':
            continue
        plotTimeVariationForGroup(
            outputFolder=input+'analysis/', column='secondsInSim',
            platformFrom=[platformFrom], platformTo=[platformTo],
            input_list=input_list
        )

    # for area in areas:
    #     plotFrameAreaAgents(
    #         input+'analysis/agentsinarea'+str(area)+'.png',
    #         area, 8, 30,
    #         input_list=input_list
    #     )
    #
    # framesDic = {}
    # for input in input_list:
    #     for area in areas:
    #         framesDic[input['maxagents_frame_area_'+str(area)]] = input['label']+'_area_'+str(area)
    #
    # print(framesDic)

    #nameEarlyAgents(input_list, 'Dircksenstr.', 'U8')

    #plotAreaDensity(input_list, areas, 8, input+'analysis/')

    #plot_minAreas(areas, input_list, qualities, input+'analysis/')



