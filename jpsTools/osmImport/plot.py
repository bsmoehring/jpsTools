'''
Created on 21.11.2017

@author: user
'''
from matplotlib import pyplot
from data import Output

def plot(transform):
    
    for poly in Output.polygons.itervalues():
        fig = pyplot.figure(1, figsize=(5,5), dpi=90)
        x, y = poly.exterior.   xy
        ax = fig.add_subplot(111)
        ax.plot(x, y, color='#6699cc', alpha=0.7,
                linewidth=3, solid_capstyle='round', zorder=2)
        ax.set_title('Polygon')
        