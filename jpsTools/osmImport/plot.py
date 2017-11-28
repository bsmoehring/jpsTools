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
             
            ax = self.fig.add_subplot(111)
            x, y = poly.exterior.xy 
            ax.plot(x, y, color='#6699cc', alpha=0.7,
                    linewidth=1, solid_capstyle='round', zorder=2)
            ax.set_title(osmId)
            
        for transition in Output.transitionlst:
            
            if transition.line.geom_type == shapely.Polygon:
                x, y = transition.line.exterior.xy 
            else:
                x, y = transition.line.coords.xy
                ax = self.fig.add_subplot(111)
                ax.plot(x, y, color='#c62b2b', alpha=0.7,
                        linewidth=2, solid_capstyle='round', zorder=2)
            ax.set_title(transition.osmid1)
    
        pyplot.axis('equal')
        pyplot.show()
