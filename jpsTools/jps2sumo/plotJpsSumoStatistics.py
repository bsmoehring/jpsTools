from xml.etree import ElementTree as ET
import pandas as pd
import numpy as np

def main(input_folder):

    columns = ['seconds', 'length', 'duration', 'routeLength']

    changes = pd.read_csv(
        input_folder+'timedistance_withsumo.csv', sep=';', index_col=0 ,
        converters={'agent_id': int, 'time': float, 'seconds':float, 'length': float,
                    'depart':float, 'duration':float, 'routeLength':float, 'timeLoss':float}
    )
    changes.dropna(subset=['seconds'])

    print(changes.mean())

if __name__ == "__main__":

    main('/media/bsmoehring/Data/wichtiges/arbeit/dlr/alexanderplatz_sumo/from_jupedsim/2/')