'''
Created on 21.11.2017

@author: user
'''
from matplotlib import pyplot
from shapely.geometry.polygon import LinearRing, Polygon
from data import Output
from constants import shapely

class ElementPlotter(object):
    
    def __init__(self, transform):
        self.transform = transform
        self.fig = pyplot.figure(1, figsize=(50,50), dpi=90)
    
    def plot(self):
        for osmId, poly in Output.polygons.iteritems():
            
            if poly.geom_type == shapely.Polygon:
                x, y = poly.exterior.xy 
            else: 
                print 'Problem handling ', poly
                continue
            
            ax = self.fig.add_subplot(111)
            ax.plot(x, y, color='#6699cc', alpha=0.7,
                    linewidth=1, solid_capstyle='round', zorder=2)
            ax.set_title(osmId)
            
        for transition in Output.transitionlst:
            
            if transition.line.geom_type == shapely.Polygon:
                x, y = transition.line.exterior.xy 
            elif transition.line.geom_type == shapely.LineString:
                x, y = transition.line.coords.xy
            else: 
                print 'Problem handling ', transition.line, transition.osmid1, transition.osmid2
                continue
            
            ax = self.fig.add_subplot(111)
            ax.plot(x, y, color='#c62b2b', alpha=0.7,
                    linewidth=2, solid_capstyle='round', zorder=2)
            ax.set_title(transition.osmid1)
    
        pyplot.axis('equal')
        pyplot.show()
