'''
Created on 10.11.2017

@author: user
'''
from shapely.geometry import LineString
from shapely.geometry.base import CAP_STYLE

def main():
    stepsl = LineString([[99.5093116342, 40.3749876982], [103.91359981, 31.703782076]])
    stepsd = stepsl.buffer(2.0, cap_style=CAP_STYLE.flat) 
    
    print stepsl
    print stepsd
    

if __name__ == '__main__':
    main()