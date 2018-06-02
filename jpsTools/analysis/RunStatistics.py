import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import itertools
import math
#from Agents import Agents, Source
#from constants import jps

def plotTimeVariationForGroup(outputFolder, platformFrom, platformTo, inputCsvBase, inputCsvProg1):

    # assert isinstance(agents, Agents)
    #
    # changesList = []
    #
    # for agentId, source in agents.agents_sources.sourcesDic.items():
    #     assert(source, Source)
    #     if source.platformFrom == platformFrom and source.platformTo == platformTo:
    #         changesList.append(source)
    print(platformFrom, platformTo)

    changesBase = pd.read_csv(inputCsvBase, sep=';', converters={'secondsInSim':float})
    changesProg1 = pd.read_csv(inputCsvProg1, sep=';', converters={'secondsInSim':float})
    #changesProg2 = pd.read_csv(inputCsvProg2, sep=';', converters={'seconds':float, 'secondsBetweenZChange':float})

    selectedChangesBase = changesBase.loc[
        ((changesBase['platformFrom'] == platformFrom) & (changesBase['platformTo'] == platformTo))
        | ((changesBase['platformTo'] == platformFrom) & (changesBase['platformFrom'] == platformTo))
        & (changesBase['secondsInSim'] > 20)
        & (changesBase['time']> 200)
        & (changesBase['secondsBetweenZChange'] > 20)
        ]
    selectedChangesProg1 = changesProg1.loc[
        ((changesProg1['platformFrom'] == platformFrom) & (changesProg1['platformTo'] == platformTo))
        | ((changesProg1['platformTo'] == platformFrom) & (changesProg1['platformFrom'] == platformTo))
        & (changesProg1['secondsInSim'] > 20)
        & (changesProg1['time']> 200)
        & (changesProg1['secondsBetweenZChange'] > 20)
        ]
    # selectedChangesProg2 = changesProg2.loc[
    #     ((changesProg2['from'] == platformFrom) & (changesProg2['to'] == platformTo))
    #     | ((changesProg2['to'] == platformFrom) & (changesProg2['from'] == platformTo))
    #     & (changesProg2['seconds'] > 20)
    #     & (changesProg2['secondsBetweenZChange'] > 20)
    #     ]
    #legend = ['Basis\nn = '+str(len(selectedChangesBase.index)), 'Prognose\nn = '+str(len(selectedChangesProg.index))]
    #counts, bins, bars = plt.hist([selectedChangesBase['seconds'], selectedChangesProg['seconds']], bins=np.arange(0, 360, 20), color=['blue', 'red'], alpha=0.5)

    plot(platformFrom, platformTo, outputFolder, 'secondsInSim', selectedChangesBase, selectedChangesProg1, None)
    #plot(platformFrom, platformTo, outputFolder, 'secondsBetweenZChange', selectedChangesBase, selectedChangesProg1, None)

def plot(platformFrom, platformTo, outputFolder, column, selectedChangesBase, selectedChangesProg1, selectedChangesProg2):

    countBase, _, _ = plt.hist(
        selectedChangesBase[column], bins=np.arange(0, 360, 10), histtype='stepfilled', color='orange',
        label='Basis'+'\nn = '+str(len(selectedChangesBase.index))+'\n\u2205 = '+str(selectedChangesBase[column].mean())
    )
    countProg1, _, _ = plt.hist(
        selectedChangesProg1[column], bins=np.arange(0, 360, 10), histtype='stepfilled', color='blue', alpha=0.5,
        label='Prognose 1'+'\nn = '+str(len(selectedChangesProg1.index))+'\n\u2205 = '+str(selectedChangesProg1[column].mean())
    )
    # countProg2, _, _ = plt.hist(
    #     selectedChangesProg2[column], bins=np.arange(0, 360, 10), histtype='stepfilled', color='black', alpha=0.5,
    #     label='Prognose 2'+'\nn = '+str(len(selectedChangesProg2.index))+'\n\u2205 = '+str(selectedChangesProg2[column].mean())
    # )
    plt.legend()
    plt.xlabel("Zeit in Sekunden")
    plt.ylabel("Häufigkeit")
    maximum = int(max(countBase.max(), countProg1.max()))
    print(maximum)
    plt.yticks(np.arange(0, maximum+1, roundup(maximum/5)))
    #plt.yticks(np.arange(0, 400, 50))
    plt.xticks(np.arange(0, 360, 50))
    plt.title(column)
    #means
    plotAverage(plt, column, selectedChangesBase, 'orange', -20)
    plotAverage(plt, column, selectedChangesProg1, 'red', 0)
    #plotAverage(plt, column, selectedChangesProg2, 'black', +20)
    #plt.show()
    plt.draw()
    plt.savefig(outputFolder + platformFrom + '_' + platformTo + '_' + column + '.png')
    plt.close()

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

def plotFrameAreaAgents(output, area, fps, inputCsvBasis, inputCsvProg1, inputCsvProg2=None):
    framesBase = pd.read_csv(inputCsvBasis, sep=';', converters={0:int, 1:int, 2:int, 3:int, 4:int, 5:int})
    selectedFramesBase = framesBase.loc[(framesBase['frame']%(fps*15) == 0)]

    framesProg1 = pd.read_csv(inputCsvProg1, sep=';', converters={0: int, 1: int, 2: int, 3: int, 4: int, 5: int})
    selectedFramesProg1 = framesProg1.loc[(framesProg1['frame'] % (fps*15) == 0)]

    framesProg2 = pd.read_csv(inputCsvProg2, sep=';', converters={0: int, 1: int, 2: int, 3: int, 4: int, 5: int})
    selectedFramesProg2 = framesProg2.loc[(framesProg2['frame'] % (fps*15) == 0)]

    # legend = ['Basis\nn = '+str(len(selectedChangesBase.index)), 'Prognose\nn = '+str(len(selectedChangesProg.index))]
    # counts, bins, bars = plt.hist([selectedChangesBase['seconds'], selectedChangesProg['seconds']], bins=np.arange(0, 360, 20), color=['blue', 'red'], alpha=0.5)

    plt.plot(selectedFramesBase['frame']/fps, selectedFramesBase[str(area)], color='orange', label='Basis', alpha=0.9)
    plt.plot(selectedFramesProg1['frame']/fps, selectedFramesProg1[str(area)], color='red', label='Prognose 1', alpha=0.9)
    plt.plot(selectedFramesProg2['frame']/fps, selectedFramesProg2[str(area)], color='black', label='Prognose 2', alpha=0.9)

    #plt.xticks(np.arange(0, 1801, 200))

    plt.legend()

    plotMax(plt, selectedFramesBase, area, 'orange', fps)
    plotMax(plt, selectedFramesProg1, area, 'red', fps)
    plotMax(plt, selectedFramesProg2, area, 'black', fps)

    plt.title('Bereich '+str(area)[0])
    plt.xlabel("Zeit in Sekunden")
    plt.ylabel("Anzahl Agenten im Bereich")
    #plt.show()
    #plt.draw()
    plt.savefig(output)
    plt.close()

def plotMax(plt, df, area, color, fps):

    maxY = df[str(area)].max()
    maxY_X = df.loc[df[str(area)].idxmax()]['frame']
    plt.axvline(x=maxY_X / fps, ymax=maxY / plt.axes().get_ylim()[1], color=color, linestyle='dashed')
    plt.text(x=maxY_X / fps, y=0,
             s='Sekunde \n'+str(int(round(maxY_X/fps, 0))),
             horizontalalignment='center',
             verticalalignment='center',
             color=color,
             bbox=dict(facecolor='white', alpha=1.0)
    )
    ylim = plt.axes().get_ylim()[1]
    plt.text(x=maxY_X/fps, y= 0.9*(maxY/ylim*ylim),
             s='Max: '+str(maxY),
             horizontalalignment='center',
             verticalalignment='center',
             color=color,
             bbox=dict(facecolor='white', alpha=1.0)
    )
    mean = int(round(df[str(area)].mean(),0))
    plt.text(x=plt.axes().get_xlim()[1], y= 1.0*(mean/ylim*ylim),
             s='\u2205: '+str(mean),
             horizontalalignment='center',
             verticalalignment='center',
             color=color,
             bbox=dict(facecolor='white', alpha=1.0)
    )

if __name__ == "__main__":

    platforms=['S', 'Regio', 'U2', 'U5', 'U8']

    input= '/media/bsmoehring/Data/wichtiges/tuberlin/masterarbeit/runs/'
    inputCsvBasis = input + '0_ipfDemandBasic/'
    inputCsvProg1 = input + '1_ipfDemandProg1/'
    inputCsvProg2 = input + '2_ipfDemandProg2/'
    #
    #plotTimeVariationForGroup(outputFolder=input + 'analysis/', platformFrom='Dircksenstr.', platformTo='U8', inputCsvBase=inputCsvBasis,
    #                          inputCsvProg1=inputCsvProg1, inputCsvProg2=None)

    # for platformFrom, platformTo in itertools.combinations(platforms, 2):
    #     if platformFrom == 'S' and platformTo == 'Regio':
    #         continue
    #     plotTimeVariationForGroup(
    #         outputFolder=input+'analysis/',
    #         platformFrom=platformFrom, platformTo=platformTo,
    #         inputCsvBase=inputCsvBasis+'changeTimes.csv',
    #         inputCsvProg1=inputCsvProg1+'changeTimes.csv'
    #     )

    areas = [11, 21, 31]
    for area in areas:
        plotFrameAreaAgents(
            input+'analysis/area_'+str(area)+'.png',
            area, 8,
            inputCsvBasis+'frameStatistics.csv',
            inputCsvProg1+'frameStatistics.csv',
            inputCsvProg2+'frameStatistics.csv'
        )



