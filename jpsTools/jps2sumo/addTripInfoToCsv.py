from xml.etree import ElementTree as ET
import pandas as pd
import numpy as np

def main(input_folder):

    columns = ['depart', 'duration', 'routeLength', 'timeLoss']

    changes = pd.read_csv(
        input_folder+'timedistance.csv', sep=';', index_col=0,
        converters={'agent_id': int, 'time': int, 'secondsInSim':float, 'length': float}
    )
    for column in columns:
        changes[column] = np.nan


    file = open(input_folder+'tripinfo.xml')
    for event, elem in ET.iterparse(file, events=['end']):
        assert isinstance(elem, ET.Element)

        if elem.tag == 'personinfo':
            id = int(elem.attrib['id'])
            print(id)

            if id in changes.index:
                walk = elem.find('walk')
                for column in columns:
                    item = walk.attrib[column]
                    changes.at[id, column] = item

            elem.clear()
    file.close()

    changes.to_csv(input_folder+'timedistance_withsumo.csv', sep=";")

if __name__ == "__main__":

    main('/media/bsmoehring/Data/wichtiges/arbeit/dlr/alexanderplatz_sumo/from_jupedsim/2/')