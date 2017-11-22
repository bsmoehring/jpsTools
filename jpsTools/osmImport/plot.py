'''
Created on 21.11.2017

@author: user
'''
from matplotlib import pyplot
from data import Output
from matplotlib.pyplot import gray

def plot(transform):
    
    fig = pyplot.figure(1, figsize=(50,50), dpi=90)
    i = 121
    
    for osmId, poly in Output.polygons.iteritems():
        
        ax = fig.add_subplot(i)
        i = i+1
        x, y = poly.exterior.xy
        ax.plot(x, y, zorder=1, linewidth=3, alpha=1)
        
    pyplot.show()
