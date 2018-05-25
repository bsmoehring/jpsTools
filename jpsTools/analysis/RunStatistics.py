import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import itertools
import math
from Agents import Agents, Source
from constants import jps

def plotTimeVariationForGroup(platformFrom, platformTo, inputCsvBase, inputCsvProg, outputFolder):

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
    changesProg = pd.read_csv(inputCsvProg, sep=';', converters={'seconds':float, 'secondsBetweenZChange':float})

    selectedChangesBase = changesBase.loc[
        ((changesBase['from'] == platformFrom) & (changesBase['to'] == platformTo))
        | ((changesBase['to'] == platformFrom) & (changesBase['from'] == platformTo))
        & (changesBase['seconds'] > 20)
        & (changesBase['secondsBetweenZChange'] > 20)
        ]
    selectedChangesProg = changesProg.loc[
        ((changesProg['from'] == platformFrom) & (changesProg['to'] == platformTo))
        | ((changesProg['to'] == platformFrom) & (changesProg['from'] == platformTo))
        & (changesProg['seconds'] > 20)
        & (changesProg['secondsBetweenZChange'] > 20)
        ]
    #legend = ['Basis\nn = '+str(len(selectedChangesBase.index)), 'Prognose\nn = '+str(len(selectedChangesProg.index))]
    #counts, bins, bars = plt.hist([selectedChangesBase['seconds'], selectedChangesProg['seconds']], bins=np.arange(0, 360, 20), color=['blue', 'red'], alpha=0.5)

    plot('seconds', selectedChangesBase, selectedChangesProg, platformFrom, platformTo, outputFolder)
    plot('secondsBetweenZChange', selectedChangesBase, selectedChangesProg, platformFrom, platformTo, outputFolder)

def plot(column, selectedChangesBase, selectedChangesProg, platformFrom, platformTo, outputFolder):

    countBase, _, _ = plt.hist(selectedChangesBase[column], bins=np.arange(0, 360, 10), histtype='stepfilled', color='b', label='Basis\nn = '+str(len(selectedChangesBase.index)))
    countProg, _, _ = plt.hist(selectedChangesProg[column], bins=np.arange(0, 360, 10), histtype='stepfilled', color='r', alpha=0.5, label='Prognose\nn = '+str(len(selectedChangesProg.index)))
    plt.legend()
    plt.xlabel("Zeit in Sekunden")
    plt.ylabel("Häufigkeit")
    maximum = int(max(countBase.max(), countProg.max()))
    print(maximum)
    plt.yticks(np.arange(0, maximum+1, roundup(maximum/5)))
    #plt.yticks(np.arange(0, 400, 50))
    plt.xticks(np.arange(0, 360, 50))
    plt.title(column)
    #means
    plotAverage(plt, column, selectedChangesBase, 'blue', -12)
    plotAverage(plt, column, selectedChangesProg, 'red', +12)
    #plt.show()
    plt.draw()
    plt.savefig(outputFolder + platformFrom + '_' + platformTo + '_' + column + '.png')
    plt.close()

def roundup(x):
    return int(math.ceil(x / 10.0)) * 10


def plotAverage(plt, column, changes, color, offset):
    mean = changes[column].mean()
    plt.axvline(x=mean, color=color, linestyle='dashed')
    print(mean)
    plt.text(mean+offset, plt.gca().get_ylim()[1]/2, '\u2205 \n' + str(int(round(mean, 0))),
             horizontalalignment='center',
             verticalalignment='center',
             color=color,
             bbox=dict(facecolor='white', alpha=0.9))

if __name__ == "__main__":

    platforms=['S', 'Regio', 'U2', 'U5', 'U8']

    input= '/media/bsmoehring/Data/wichtiges/tuberlin/masterarbeit/runs/'
    inputCsvBasis = input + '0_ipfDemandBasic_15130/changeTimes.csv'
    inputCsvProg = input + '1_ipfDemandProg1/changeTimes.csv'

    plotTimeVariationForGroup(platformFrom='Dircksenstr.', platformTo='U8', inputCsvBase=inputCsvBasis,
                              inputCsvProg=inputCsvProg, outputFolder=input + 'analysis/')

    for platformFrom, platformTo in itertools.combinations(platforms, 2):
        if platformFrom == 'S' and platformTo == 'Regio':
            continue
        plotTimeVariationForGroup(platformFrom=platformFrom, platformTo=platformTo, inputCsvBase=inputCsvBasis,
                                  inputCsvProg=inputCsvProg, outputFolder=input+'analysis/')
