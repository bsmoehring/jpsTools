import geometry_reader
import geometry_writer
from geometry import Geometry
import sys

def copy_jps_geo(inputfile, outputfile):

    geo = geometry_reader.read_jps_geometry(inputfile)
    assert isinstance(geo, Geometry)
    geometry_writer.write_geometry(geo, outputfile)

if      __name__ == "__main__":

    copy_jps_geo('./../osm2jps/resources/jps_geo.xml', './../osm2jps/resources/jps_geo_copy.xml')