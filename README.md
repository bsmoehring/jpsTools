# jpsTools

tool for converting osm-data into jupedsim geometry files

# Requirements:

- Python3
- shapely
- pyproj
- matplotlib
- lxml


# How to:

- Download openstreetmap data for a specific area.
  In terms of being able to manually edit the data I recommend using `JOSM` (JavaOpenStreetMap-Editor) 
- Save the data of your choice as an .osm file
- Run jpsTools.osmImport.main() with command-line argmuents [1] the folder of your osm file and [2] the filename
    e.g. 'resources/ Meckesheim.osm'

