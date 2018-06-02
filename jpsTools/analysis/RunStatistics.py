import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import itertools
import math
#from Agents import Agents, Source
#from constants import jps

def plotTimeVariationForGroup(outputFolder, column, platformFrom, platformTo, input_list=[]):

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

    for input in input_list:

        file = input[0]+'changeTimes.csv'
        label = input[1]
        color = input[2]
        opacity = input[3]

        changes = pd.read_csv(file, sep=';', converters={'secondsInSim':float, 'time':int})
        selectedChanges = changes.loc[
            ((changes['platformFrom'] == platformFrom) & (changes['platformTo'] == platformTo))
            | ((changes['platformTo'] == platformFrom) & (changes['platformFrom'] == platformTo))
            & (changes[column] > 20)
            & (changes['time'] >= 200)
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

def plotFrameAreaAgents(output, area, fps, input_list = []):
    for input in input_list:

        file = input[0]+'frameStatistics.csv'
        label = input[1]
        color = input[2]
        frames = pd.read_csv(file, sep=';', converters={0:int, 1:int, 2:int, 3:int, 4:int, 5:int})
        selectedFrames = frames.loc[
            (frames['frame']%(fps*15) == 0)
        ]

        plt.plot(selectedFrames['frame']/fps, selectedFrames[str(area)], color=color, label=label, alpha=0.9)
        plotMax(plt, selectedFrames, area, color, fps)

    plt.legend()

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
    ylim = plt.axes().get_ylim()[1]
    plt.axvline(x=maxY_X / fps, ymax=maxY/ylim*ylim, color=color, linestyle='dashed')
    plt.text(x=maxY_X / fps, y=0,
             s='Sekunde \n'+str(int(round(maxY_X/fps, 0))),
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
    plt.text(x=0., y= 1.0*(mean/ylim*ylim),
             s='\u2205: '+str(mean),
             horizontalalignment='center',
             verticalalignment='center',
             color=color,
             bbox=dict(facecolor='white', alpha=1.0)
    )

if __name__ == "__main__":

    platforms=['S', 'Regio', 'U2', 'U5', 'U8']

    input= '/media/bsmoehring/Data/wichtiges/tuberlin/masterarbeit/runs/'
    inputBasis = (input + '0_ipfDemandBasic/', 'Basis', 'grey', 0.5)
    inputProg1 = (input + '1_ipfDemandProg1/', 'Prognose 1', 'blue', 0.25)
    inputProg2 = (input + '2_ipfDemandProg2/', 'Prognose 2', 'orange', 0.4)
    input_list = [inputBasis, inputProg1]
    #
    #plotTimeVariationForGroup(outputFolder=input + 'analysis/', platformFrom='Dircksenstr.', platformTo='U8', inputCsvBase=inputCsvBasis,
    #                          inputCsvProg1=inputCsvProg1, inputCsvProg2=None)

    for platformFrom, platformTo in itertools.combinations(platforms, 2):
        if platformFrom == 'S' and platformTo == 'Regio':
            continue
        plotTimeVariationForGroup(
            outputFolder=input+'analysis/', column='secondsInSim',
            platformFrom=platformFrom, platformTo=platformTo,
            input_list=input_list
        )

    areas = [11, 21, 31]
    for area in areas:
        plotFrameAreaAgents(
            input+'analysis/area_'+str(area)+'.png',
            area, 8,
            input_list=input_list
        )



