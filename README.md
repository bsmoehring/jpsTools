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
- Run jpsTools.osmImport.main() with command-line argmuents
    [1] the folder of your osm file and
    [2] the filename e.g. 'resources/ Meckesheim.osm'
    [3] 'handle' if you want jpsTools to translate ways by attributes polygons and define transitions.
        leave [3] empty if you only want to convert a finished and edited .osm file.

# Configurations

- inside jpsTools.osmImport.main() modify or define as many filterTags and unhandleTags as you want.
   Depending on your the local osm community and their 'dialects' tagging might differ
- filterTags describe which elements to load and handle from your osm file.
   If an osm element contains the key-value pair it will be used.
- unhandleTags are currently used for nodes, which aren't supposed to be adjusted.
   e.g. Tag: 'elevator'='yes', it is not our aim to merge paths on either side of an elevator.
- Check what tags you want to translate by playing around with your downloaded elements in JOSM
- The tag 'width' = XX describes the width of an element in meters. If you know the shapes of you environment you can
   add the tag to any element and jpsTools will use the value to buffer its size.
- Closed ways (first node equals last node) tagged 'area'='yes' are defined as areas and will not be adjusted in size.

