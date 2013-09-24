OSM Street Processing
==========

This Rube Goldberg machine of a repo includes a set of utilities that, together, take in an OpenStreetMap XML file and put it through a meat grinder and end up with a set of MySQL databases containing a list of streets and their geometries, ready to add historical information.

How does it work?
-----------------

First, get an OSM extract of an area you're interested in.  A good resource for that is:  
http://metro.teczno.com/

As an optional additional step, you can reduce the extract down to just the city limits, or some arbitrary boundary.  Those metro extracts are very generous, covering large areas, and if you try to process the whole thing, your computer will probably catch fire.

As an example, to bound the extract to the city limits of Seattle, you can do the following:

1. Install Osmosis: http://wiki.openstreetmap.org/wiki/Osmosis

2. Go to http://overpass-turbo.eu/, zoom to the Seattle area, and run a query to search for a relation with the name "Seattle":

        <query type="relation">
            <has-kv k="name" v="Seattle"/>
            <bbox-query {{bbox}}/>
        </query>
        <union>
            <item/>
            <recurse type="down"/>
        </union>    
        <print/>
        
3. If the boundary shown on the map looks right, click "Export," choose "Raw Data," and look through the export for the relation ID of Seattle:

        <relation id="237385">

4. To get a .poly file based on the relation ID, use this handy tool: http://osm102.openstreetmap.fr/~jocelyn/polygons/index.py

5. Download the .poly result.

6. Run osmosis using the original .osm file you downloaded and the bounding .poly file you downloaded:

        osmosis --read-xml file="seattle-original.osm" --bounding-polygon file="seattle.poly" --write-xml file="seattle-citylimits.osm"

Processing the XML
------------------
Once you've got an XML file covering the area you want, you can process it.  Run the shell script `split-osm.sh`:

        ./split-osm.sh

It will prompt you for an XML filename (you can also supply the filename as a command line argument if you want).  Then it will ask you which processing steps you want.  You probably want all of them, unless you're debugging.  The script is verbose throughout, it will tell you what it's doing, and for parts where it's processing items in the database, it will print a running log of each one.

* **Generate new XML files?** This will split your XML file into two smaller files: a file with just nodes, and a file with just highways.  This step is used because trying to process the entire XML file is rough if you're talking about a big place, like Chicago or Los Angeles or London.
* **Generate new TSV files?** This will process the XML files you just created into three TSVs.  The first is a list of nodes with latitudes and longitudes.  The second is a list of "ways" with street information (name, whether it's a freeway or an alley, etc.).  The third is a node map that tells you what nodes a given way is made of.
* **Create a new MySQL import script?** This will create a script to import those TSVs into a new database.  You'll have to supply a suffix, like "sea" for Seattle.  The database will be named `streets_[suffix]`, like `streets_sea`.
* **Execute the script?** This will run the import script.  You'll have to supply a DB username and password that has permissions to create and populate a database.
* **Generate polylines now?** This will go through the ways in the new database, and for each one, it will produce a JSON-formatted polyline or multipolyline of latitudes and longitudes based on its nodes.  These polylines can then be put straight into Leaflet to draw them.
* **Set numeric street levels?** Assigns a numeric value of 1-5 to each street based on its OpenStreetMap road type.  1 is a major highway, 5 is a tiny alley.  Useful for weighting lines on a map.
* **Fill in missing name bases?** A lot of streets in OpenStreetMap come with a name_base field.  For example, "Washington Street" would probably have the name base "Washington."  Some of them are blank, though.  This step attempts to fill in missing ones by discarding prefixes and suffixes and stray punctuation.
* **Delete generated files?** Deletes all the files that have been created by the above steps (it won't delete your starting XML files, just things the script has created).


Infrequently Asked Questions
----------------------------

**Why is this so complicated?**  
A mix of reasons.  Some are my own foolishness/laziness.  But doing it stepwise, outputting to lots of intermediate files along the way, makes it easier to ensure that what's supposed to happen is actually happening at each step.  This is important when you're crunching 2 GB of sometimes messy data.  Lots of weird exceptions come up.

**Why MySQL?**  
This could easily be modified for PostgreSQL, I'm sure.  I know that's the way to go for GIS stuff, but my old habits die hard, and a plain database works fine for this scenario because I'm not actually doing any spatial joins or anything like that.  If I had experience with PostgreSQL I'd have used that instead.

**What do I do now?**  
Coming soon: A generalized browser-based editor for the DB for users to input/edit historical information, de-dupe and merge streets, add landmarks.