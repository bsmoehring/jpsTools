import matplotlib.pyplot as plt
from shapely.geometry import Polygon

from Agents import Agents, Area

if __name__ == "__main__":
    agents = Agents()

    for area in agents.counts.area_list:
        assert isinstance(area, Area)
        poly = Polygon(area.coord_list)
        x, y = poly.exterior.xy
        plt.plot(x, y, color='#6699cc', alpha=0.7,
                linewidth=3, solid_capstyle='round', zorder=2)
        plt.show()
