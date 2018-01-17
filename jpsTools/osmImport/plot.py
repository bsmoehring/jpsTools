'''
Created on 21.11.2017

@author: bsmoehring
'''
from matplotlib import pyplot
from data import Output
from shapely import geometry

class ElementPlotter(object):
    
    def __init__(self, transform):
        self.transform = transform
        self.fig = pyplot.figure(1, figsize=(50,50), dpi=90)
    
    def plotOutput(self):
        for osmId, poly in Output.polygons.iteritems():
            
            if isinstance(poly, geometry.Polygon):
                x, y = poly.exterior.xy 
            else: 
                print 'Problem handling ', poly
                continue
            
            ax = self.fig.add_subplot(111)
            ax.plot(x, y, color='#6699cc', alpha=0.7,
                    linewidth=1, solid_capstyle='round', zorder=2, marker='o')
            ax.set_title(osmId)
            
        #=======================================================================
        # for transition in Output.transitionlst:
        #      
        #     try:
        #         x1, y1 = self.xy(transition.line)
        #         ax = self.fig.add_subplot(111)
        #         ax.plot(x1, y1, color='#c62b2b', alpha=0.7,
        #                 linewidth=2, solid_capstyle='round', zorder=4, marker='o')
        #     except (AttributeError):
        #         if isinstance(transition, geometry.Polygon):
        #             x, y = transition.exterior.xy
        #         else:
        #             x, y = self.xy(transition.line)
        #         ax = self.fig.add_subplot(111)
        #         ax.plot(x, y, color='#c62b2b', alpha=0.7,
        #         linewidth=2, solid_capstyle='round', zorder=4, marker='o')
        #=======================================================================
    
        pyplot.axis('equal')
        pyplot.show()
        
    def plotElement(self, object):
        pass
    
    def xy(self, elem):
        if isinstance(elem, geometry.Polygon):
            x, y = elem.exterior.xy 
        elif isinstance(elem, geometry.LineString):
            x, y = elem.coords.xy
        elif isinstance(elem, geometry.Point):
            x, y = elem.xy
        else:
            print 'Cant plot element ', elem
        return x, y
