# jpsTools

tool for converting osm-data into jupedsim geometry files

# Requirements:

- Python
- shapely
- pyproj
- matplotlib
- lxml


# How to:

- Download openstreetmap data for a specific area.
  In terms of being able to manually edit the data I recommend using `JOSM` (JavaOpenStreetMap-Editor) 
- Save the data of your choice as an .osm file
- Define input and output in config.Config.inputFile and config.Config.outputPath
- Run jpsTools.osmImport.main()
