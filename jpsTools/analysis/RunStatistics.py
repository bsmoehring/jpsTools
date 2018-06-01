import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import itertools
import math
#from Agents import Agents, Source
#from constants import jps

def plotTimeVariationForGroup(platformFrom, platformTo, inputCsvBase, inputCsvProg1, inputCsvProg2, outputFolder):

    # assert isinstance(agents, Agents)
    #
    # changesList = []
    #
    # for agentId, source in agents.agents_sources.sourcesDic.items():
    #     assert(source, Source)
    #     if source.platformFrom == platformFrom and source.platformTo == platformTo:
    #         changesList.append(source)
    print(platformFrom, platformTo)

    changesBase = pd.read_csv(inputCsvBase, sep=';', converters={'seconds':float, 'secondsBetweenZChange':float})
    changesProg1 = pd.read_csv(inputCsvProg1, sep=';', converters={'seconds':float, 'secondsBetweenZChange':float})
    changesProg2 = pd.read_csv(inputCsvProg2, sep=';', converters={'seconds':float, 'secondsBetweenZChange':float})

    selectedChangesBase = changesBase.loc[
        ((changesBase['from'] == platformFrom) & (changesBase['to'] == platformTo))
        | ((changesBase['to'] == platformFrom) & (changesBase['from'] == platformTo))
        & (changesBase['seconds'] > 20)
        & (changesBase['secondsBetweenZChange'] > 20)
        ]
    selectedChangesProg1 = changesProg1.loc[
        ((changesProg1['from'] == platformFrom) & (changesProg1['to'] == platformTo))
        | ((changesProg1['to'] == platformFrom) & (changesProg1['from'] == platformTo))
        & (changesProg1['seconds'] > 20)
        & (changesProg1['secondsBetweenZChange'] > 20)
        ]
    selectedChangesProg2 = changesProg2.loc[
        ((changesProg2['from'] == platformFrom) & (changesProg2['to'] == platformTo))
        | ((changesProg2['to'] == platformFrom) & (changesProg2['from'] == platformTo))
        & (changesProg2['seconds'] > 20)
        & (changesProg2['secondsBetweenZChange'] > 20)
        ]
    #legend = ['Basis\nn = '+str(len(selectedChangesBase.index)), 'Prognose\nn = '+str(len(selectedChangesProg.index))]
    #counts, bins, bars = plt.hist([selectedChangesBase['seconds'], selectedChangesProg['seconds']], bins=np.arange(0, 360, 20), color=['blue', 'red'], alpha=0.5)

    plot('seconds', selectedChangesBase, selectedChangesProg1, selectedChangesProg2, platformFrom, platformTo, outputFolder)
    plot('secondsBetweenZChange', selectedChangesBase, selectedChangesProg1, selectedChangesProg2, platformFrom, platformTo, outputFolder)

def plot(column, selectedChangesBase, selectedChangesProg1, selectedChangesProg2, platformFrom, platformTo, outputFolder):

    countBase, _, _ = plt.hist(
        selectedChangesBase[column], bins=np.arange(0, 360, 10), histtype='stepfilled', color='orange',
        label='Basis'+'\nn = '+str(len(selectedChangesBase.index))+'\n\u2205 = '+str(selectedChangesBase[column].mean())
    )
    countProg1, _, _ = plt.hist(
        selectedChangesProg1[column], bins=np.arange(0, 360, 10), histtype='stepfilled', color='red', alpha=0.5,
        label='Prognose 1'+'\nn = '+str(len(selectedChangesProg1.index))+'\n\u2205 = '+str(selectedChangesProg1[column].mean())
    )
    countProg2, _, _ = plt.hist(
        selectedChangesProg2[column], bins=np.arange(0, 360, 10), histtype='stepfilled', color='black', alpha=0.5,
        label='Prognose 2'+'\nn = '+str(len(selectedChangesProg2.index))+'\n\u2205 = '+str(selectedChangesProg2[column].mean())
    )
    plt.legend()
    plt.xlabel("Zeit in Sekunden")
    plt.ylabel("Häufigkeit")
    maximum = int(max(countBase.max(), countProg1.max(), countProg2.max()))
    print(maximum)
    plt.yticks(np.arange(0, maximum+1, roundup(maximum/5)))
    #plt.yticks(np.arange(0, 400, 50))
    plt.xticks(np.arange(0, 360, 50))
    plt.title(column)
    #means
    plotAverage(plt, column, selectedChangesBase, 'orange', -20)
    plotAverage(plt, column, selectedChangesProg1, 'red', 0)
    plotAverage(plt, column, selectedChangesProg2, 'black', +20)
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

def plotFrameAreaAgents(inputCsvBasis, inputCsvProg1, inputCsvProg2, area, fps):
    framesBase = pd.read_csv(inputCsvBasis, sep=';', converters={0:int, 1:int, 2:int, 3:int, 4:int, 5:int})
    selectedFramesBase = framesBase.loc[(framesBase['frame']%fps == 0)]

    framesProg1 = pd.read_csv(inputCsvProg1, sep=';', converters={0: int, 1: int, 2: int, 3: int, 4: int, 5: int})
    selectedFramesProg1 = framesProg1.loc[(framesProg1['frame'] % fps == 0)]

    framesProg2 = pd.read_csv(inputCsvProg2, sep=';', converters={0: int, 1: int, 2: int, 3: int, 4: int, 5: int})
    selectedFramesProg2 = framesProg2.loc[(framesProg2['frame'] % fps == 0)]

    # legend = ['Basis\nn = '+str(len(selectedChangesBase.index)), 'Prognose\nn = '+str(len(selectedChangesProg.index))]
    # counts, bins, bars = plt.hist([selectedChangesBase['seconds'], selectedChangesProg['seconds']], bins=np.arange(0, 360, 20), color=['blue', 'red'], alpha=0.5)

    plt.plot(selectedFramesBase['frame']/fps, selectedFramesBase[str(area)], color='orange', label='Basis', alpha=0.9)
    plt.plot(selectedFramesProg1['frame']/fps, selectedFramesProg1[str(area)], color='red', label='Prognose 1', alpha=0.9)
    plt.plot(selectedFramesProg2['frame']/fps, selectedFramesProg2[str(area)], color='black', label='Prognose 2', alpha=0.9)

    plotMax(plt, selectedFramesBase, area, 'orange', fps)
    plotMax(plt, selectedFramesProg1, area, 'red', fps)
    plotMax(plt, selectedFramesProg2, area, 'black', fps)

    plt.legend()
    plt.title('Bereich '+str(area)[0])
    plt.xlabel("Zeit in Sekunden")
    plt.ylabel("Anzahl Agenten im Bereich")
    plt.show()

def plotMax(plt, df, area, color, fps):

    maxY = df[str(area)].max()
    maxY_X = df.loc[df[str(area)].idxmax()]['frame']
    plt.axvline(x=maxY_X / fps, ymax=maxY / plt.axes().get_ylim()[1], color=color, linestyle='dashed')
    plt.text(maxY_X / fps, 0,
             s=str(maxY),
             horizontalalignment='center',
             verticalalignment='center',
             color=color,
             bbox=dict(facecolor='white', alpha=0.9)
    )
    print(plt.axes().get_ylim()[1])
    plt.text(maxY_X / fps, maxY/plt.axes().get_ylim()[1],
             s='Agenten: '+str(maxY)+'\nSekunde: '+str(int(round(maxY_X/fps, 0))),
             horizontalalignment='center',
             verticalalignment='center',
             color=color,
             bbox=dict(facecolor='white', alpha=0.9)
    )

if __name__ == "__main__":

    platforms=['S', 'Regio', 'U2', 'U5', 'U8']

    input= '/media/bsmoehring/Data/wichtiges/tuberlin/masterarbeit/runs/'
    inputCsvBasis = input + '0_ipfDemandBasic/frameStatistics.csv'
    inputCsvProg1 = input + '1_ipfDemandProg1/frameStatistics.csv'
    inputCsvProg2 = input + '2_ipfDemandProg2/frameStatistics.csv'
    #
    # plotTimeVariationForGroup(platformFrom='Dircksenstr.', platformTo='U8', inputCsvBase=inputCsvBasis,
    #                           inputCsvProg1=inputCsvProg1, inputCsvProg2=inputCsvProg2, outputFolder=input + 'analysis/')
    #
    # for platformFrom, platformTo in itertools.combinations(platforms, 2):
    #     if platformFrom == 'S' and platformTo == 'Regio':
    #         continue
    #     plotTimeVariationForGroup(platformFrom=platformFrom, platformTo=platformTo, inputCsvBase=inputCsvBasis,
    #                               inputCsvProg1=inputCsvProg1, inputCsvProg2=inputCsvProg2, outputFolder=input+'analysis/')

    area = 31
    plotFrameAreaAgents(inputCsvBasis, inputCsvProg1, inputCsvProg2, area, 8)



