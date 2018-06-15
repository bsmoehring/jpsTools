import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import itertools
import math
#from Agents import Agents, Source
#from constants import jps

def plotTimeVariationForGroup(outputFolder, column, platformFrom, platformTo,  input_list = []):

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

        changes = pd.read_csv(file, sep=';', converters={'secondsInSim':float, 'time':int})
        selectedChanges = changes.loc[
            ((changes['platformFrom'] == platformFrom) & (changes['platformTo'] == platformTo))
            | ((changes['platformTo'] == platformFrom) & (changes['platformFrom'] == platformTo))
            & (changes[column] > 20)
            & (changes['time'] >= 240)
            & ((changes['area_11'] == True) | (changes['area_21'] == True) | (changes['area_31'] == True))
            ]
        plotAverage(plt, column, selectedChanges, color, 0)

    #legend = ['Basis\nn = '+str(len(selectedChanges.index)), 'Prognose\nn = '+str(len(selectedChangesProg.index))]
    #counts, bins, bars = plt.hist([selectedChanges['seconds'], selectedChangesProg['seconds']], bins=np.arange(0, 360, 20), color=['blue', 'red'], alpha=0.5)

        maximum = plot(column, selectedChanges, color, label, opacity)
        maximum_list.append(maximum)

    plt.legend()
    plt.xlabel("Zeit in Sekunden")
    plt.ylabel("Häufigkeit")
    maximum = int(max(maximum_list))
    print(maximum)
    plt.yticks(np.arange(0, maximum+1, roundup(maximum/5)))
    #plt.yticks(np.arange(0, 400, 50))
    plt.xticks(np.arange(0, 360, 50))
    plt.title(column)
    #plt.show()
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

def plotAreaDensity(input_list, area, areas, fps, path):
    plt.rcParams.update({'font.size': 14})
    outputfile = path + 'densityinarea'+area
    column = area+'_avgA'
    #plt.title('Detail '+area[0])
    plt.xlabel('Zeit in Sekunden')
    plt.xticks(np.arange(300, 1801, 300))
    plt.yticks(np.arange(0., 3.5, 0.5))
    axes = plt.gca()
    axes.set_ylim(0.5, 3.25)
    plt.ylabel('$m^2$ / Person')

    for input in input_list:
        color = input['color']
        label = input['label']
        offset = input['offset']
        file = input['file']+'areaLoS.csv'
        converters = {'frame': int}
        for area1 in areas:
            converters[str(area1)+'_numb'] = int
            converters[str(area1)+'_minA'] = float
            converters[str(area1)+'_maxA'] = float
            converters[str(area1)+'_avgA'] = float
        frames = pd.read_csv(file, sep=';', converters=converters)
        selectedFrames = frames.loc[
            ((frames['frame'] % (fps) == 0)) & (frames['frame']>300*fps) & (frames['31_numb'] > 10)
        ]
        selectedFramesMeans = selectedFrames.groupby(
            pd.cut(selectedFrames['frame'], np.arange(0, 14000 + (20 * fps), 20 * fps))
        ).mean()
        plt.plot(
            selectedFramesMeans['frame'] / fps, selectedFramesMeans[column],
            color=color, label=label, alpha=0.9, linewidth=0.7
        )
        ylim = plt.axes().get_ylim()[1]
        mean = selectedFrames[column].mean()
        #plt.axhline(y=mean, color=color, linewidth=1.5)
        plt.text(
            x=280., y= 1.0*(mean/ylim*ylim)-offset/15,
            s='\u2205: '+str(round(mean,2)),
            horizontalalignment='center',
            verticalalignment='center',
            color=color,
            bbox=dict(facecolor='white', alpha=1.0)
        )
        minY = selectedFrames[column].min()
        minY_X = selectedFrames.loc[selectedFrames[column].idxmin()]['frame']
        plt.axvline(x=minY_X/fps, color=color, linewidth=1.5)
        # plt.text(
        #     x=minY_X/fps, y=1*plt.axes().get_ylim()[0],
        #     s='Sek: \n' + str(int(round(minY_X / fps, 0))),
        #     horizontalalignment='center',
        #     verticalalignment='center',
        #     color=color,
        #     bbox=dict(facecolor='white', alpha=1.0)
        # )
        y = (minY / ylim * ylim)-(offset/15) -0.1
        if y < 0.7: y = 0.7
        plt.text(x=minY_X / fps, y=y,
                 s=str(minY) + ' $m^2$'+'\nSek: ' + str(int(minY_X/fps)),
                 horizontalalignment='center',
                 verticalalignment='center',
                 color=color,
                 bbox=dict(facecolor='white', alpha=1.0)
                 )
        print(area, label, minY, int(minY_X))
    leg  = plt.legend()
    for legobj in leg.legendHandles:
        legobj.set_linewidth(2.0)

    plt.savefig(outputfile)
    plt.show()
    plt.close()

def runAggregateStatistics(input_csv, label):
    changes = pd.read_csv(input_csv, sep=';', converters={'secondsInSim': float, 'time': int})
    mean = round(changes['secondsInSim'].mean(), 2)
    selected_changes = changes.loc[
        (changes['time'] >= 240)
        & ((changes['area_11'] == True) | (changes['area_21'] == True) | (changes['area_31'] == True))
    ]
    selected_changes_mean = round(selected_changes['secondsInSim'].mean(), 2)
    print(
        label,
        'all:', changes.shape[0], 'mean:', mean, 'deviation', round(changes['secondsInSim'].std(),2),
        'areas', selected_changes.shape[0], 'mean:', selected_changes_mean, 'var', round(selected_changes['secondsInSim'].std(),2)
    )

if __name__ == "__main__":

    platforms=[
        'S', 'Regio', 'U2', 'U5', 'U8'
#        , 'Gontardstr.', 'Dircksenstr.', 'Tram U'
    ]
    areas = [11, 21, 31]

    input= '/media/bsmoehring/Data/wichtiges/tuberlin/masterarbeit/runs/'
    inputBasis = {'file':input + '0_ipfDemandBasic/', 'label':'Basis', 'color':'grey', 'opacity':0.4, 'offset':-2}
    inputProg1 = {'file':input + '1_ipfDemandProg1/', 'label':'Prognose 1', 'color':'blue', 'opacity':0.25, 'offset':0}
    inputProg2 = {'file':input + '2_ipfDemandProg2/', 'label':'Prognose 2', 'color':'orange', 'opacity':0.3, 'offset':+2}
    input_list = [inputBasis, inputProg1, inputProg2]

    #plotTimeVariationForGroup(
    #        outputFolder=input+'analysis/', column='secondsInSim',
    #        platformFrom='S', platformTo='U2',
    #        input_list=input_list)

    # for platformFrom, platformTo in itertools.combinations(platforms, 2):
    #     if platformFrom == 'S' and platformTo == 'Regio':
    #         continue
    #     plotTimeVariationForGroup(
    #         outputFolder=input+'analysis/', column='secondsInSim',
    #         platformFrom=platformFrom, platformTo=platformTo,
    #         input_list=input_list
    #     )
    #
    #
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

    for area in areas:
        plotAreaDensity(input_list, str(area), areas, 8, input+'analysis/')

    #for input in input_list:
    #    runAggregateStatistics(input['file']+'changeTimes.csv', input['label'])




