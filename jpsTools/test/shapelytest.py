'''
Created on 10.11.2017

@author: user
'''
from shapely.geometry import LineString, Polygon, Point
from shapely.geometry.base import CAP_STYLE

def main():
    stepsl = LineString([[99.5093116342, 40.3749876982], [103.91359981, 31.703782076]])
    stepsd = stepsl.buffer(2.0, cap_style=CAP_STYLE.flat) 
    Polygon(stepsd)
    print stepsl
    print stepsd
    print Polygon.__class__.__name__
    print stepsl.geom_type
    print stepsd.__class__.__name__
    print stepsd.area
    
    print stepsl.xy
    print list(stepsl.coords)[0][0]

if __name__ == '__main__':
    main()