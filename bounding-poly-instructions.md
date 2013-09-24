### Step 1: Get a metro area extract ###

Use http://metro.teczno.com/

Unzip it

### Step 2: Get the relation ID of the city boundaries ###

Use http://overpass-turbo.eu/

Example query:

	<query type="relation">
	  <has-kv k="name" v="New York City"/>
	  <bbox-query {{bbox}}/><!--this is auto-completed with the
	                   current map view coordinates.-->
	</query>
	<!-- added by auto repair -->
	<union>
	  <item/>
	  <recurse type="down"/>
	</union>
	<!-- end of auto repair -->
	<print/>

Go to "Export," then "Raw Data." Get the relation ID.

### Step 3: Get the bounding .poly of the relation ID ###

Use: http://osm102.openstreetmap.fr/~jocelyn/polygons/index.py

Save the .poly file

### Step 4: Use the .osm file and the .poly file to create a bounded extract ###

	osmosis --read-xml file="losangeles-all.osm" --bounding-polygon file="losangeles.poly" --write-xml file="losangeles-citylimits.osm"