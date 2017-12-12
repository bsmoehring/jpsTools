'''
Created on 21.11.2017

@author: user
'''
from matplotlib import pyplot
from data import Output
from constants import shapely

class ElementPlotter(object):
    
    def __init__(self, transform):
        self.transform = transform
        self.fig = pyplot.figure(1, figsize=(50,50), dpi=90)
    
    def plotOutput(self):
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
            
            try:
                x1, y1 = self.xy(transition.line)
                ax = self.fig.add_subplot(111)
                ax.plot(x1, y1, color='#c62b2b', alpha=0.7,
                        linewidth=2, solid_capstyle='round', zorder=4)
            except (AttributeError):
                if transition.geom_type == shapely.Polygon:
                    x, y = transition.exterior.xy
                else:
                    x, y = self.xy(transition.line)
                ax = self.fig.add_subplot(111)
                ax.plot(x, y, color='#c62b2b', alpha=0.7,
                linewidth=2, solid_capstyle='round', zorder=4)
            #===================================================================
            # else: 
            #     print 'Problem handling ', transition.line, transition.osmid1, transition.osmid2
            #     continue
            #===================================================================
    
        pyplot.axis('equal')
        pyplot.show()
        
    def plotElement(self, object):
        pass
    
    def xy(self, elem):
        if elem.geom_type == shapely.Polygon:
            x, y = elem.exterior.xy 
        elif elem.geom_type == shapely.LineString:
            x, y = elem.coords.xy
        elif elem.geom_type == shapely.Point:
            x, y = elem.xy
        else:
            print 'Cant plot element ', elem
        return x, y
