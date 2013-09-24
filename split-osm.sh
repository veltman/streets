#! /bin/bash

if [ $# -gt 0 ];
then
	filename=$1
else
	read -p "What's the .osm filename? " filename
fi

if [[ $filename =~ ^/ ]];
then
	absolutepath="$(dirname ${filename})/"
else
	absolutepath="$(dirname $( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/$filename)/"
fi

if [ -f $filename ] && [ ${#filename} -gt 0 ];
then	
	read -p "Generate new XML files (y/n)? " answer
	if [[ $answer =~ ^[Yy]$ ]];
	then
		
		# These steps could theoretically be skipped, but splitting the XML into different files for nodes and highways improves performance a lot. Trying to churn through 2 GB of XML for a city like Chicago causes problems.

		sed -ne '/<node/p' $filename > "$filename.nodes.xml"
		echo "Created nodes-only XML file: $filename.nodes.xml"	

		#This works but leaves excess tags in: head -n 2 $filename > "$filename.ways.xml" && sed -ne '/<\/\?osm\|<\/\?way\|<\/\?nd\|<\/\?tag\|<?xml/p' $filename | sed -n '/<way/,$p' >> "$filename.ways.xml"
		head -n 2 $filename > "$filename.ways.xml" && sed -ne '/<\/\?osm\|<\/\?way\|<nd\|<tag k="name\|<tag k="highway\|<tag k="tiger:name_type\|<tag k="tiger:name_base\|<?xml/p' $filename | sed 's/ \(timestamp\|version\|uid\|user\|changeset\)="[^"]\+"//g' | sed -n '/<way/,$p' >> "$filename.ways.xml"
		echo "Created ways-only XML file: $filename.ways.xml"
		
		#Take out non-highway ways for faster processing
		python remove-non-highways.py "$filename.ways.xml" > "$filename.highways.xml"		
		echo "Created ways-only XML file with highways only: $filename.highways.xml"

		#Don't need this anymore		
		#head -n 2 $filename > "$filename.nodemap.xml" && sed -ne '/<\/\?osm\|<\/\?way\|<nd\|<tag k="highway\|<?xml/p' $filename | sed 's/ \(timestamp\|version\|uid\|user\|changeset\)="[^"]\+"//g' | sed -n '/<way/,$p' >> "$filename.nodemap.xml"
		#python remove-non-highways.py "$filename.nodemap.xml" > "$filename.nodemap.xml"
		#echo "Created nodemap XML file: $filename.nodemap.xml"		

	fi

	read -p "Generate new TSV files (y/n)? " answer
	if [[ $answer =~ ^[Yy]$ ]];
	then	

		echo -n "Extracting nodes... "

		#Slower method
		#python extract-nodes.py "$filename.nodes.xml" > "$filename.nodes.tsv"

		#Old brute force method
		#sed -n '/<node/p' $filename.nodes.xml | sed 's/ \(timestamp\|version\|uid\|user\|changeset\)="[^"]\+"//g' | sed 's/ id="//g' | sed 's/<node//' | sed 's/" \(lat\|lon\)="/\t/g' | sed '/\/\?>//g' | sed 's/"\| //g' > $filename.nodes.tsv

		#New brute force method
		sed -n '/<node/p' $filename.nodes.xml | sed 's/ \(timestamp\|version\|uid\|user\|changeset\)="[^"]\+"//g' | sed 's/<node id="//g' | sed 's/\/\?>//g' | sed 's/" \(lat\|lon\)="/\t/g'  | sed 's/"\| //g' > $filename.nodes.tsv
		echo "Extracted nodes: $filename.nodes.tsv"

		echo -n "Extracting ways... "
		python extract-ways.py "$filename.highways.xml" > "$filename.ways.tsv"
		echo "Extracted ways: $filename.ways.tsv"

		echo -n "Extracting node map... "
		python extract-node-map.py "$filename.highways.xml" > "$filename.nodemap.tsv"
		echo "Extracted node map: $filename.nodemap.tsv"

	fi



	read -p "Create a new MySQL import script (y/n)? " answer
	if [[ $answer =~ ^[Yy]$ ]];
	then

		echo "Using absolute path: $absolutepath"

		read -p "DB suffix (e.g. 'la'): " suffix

		# Shouldn't need this, automatic absolute path detection now provided at the top
		#read -p "Absolute path to the .tsv files (e.g. '/projects/streets/la/')? " absolutepath

		osmfile=$(basename $filename)

		# Absolute path used in scripts to get around LOAD DATA INFILE quirks
		sed "s/SUFFIX/$suffix/g" streets.sql | sed "s@ABSOLUTEPATH@$absolutepath@g" | sed "s@FILENAME@$osmfile@g" > "$filename.sql"
		echo "Created SQL file: $filename.sql"

		sed "s/SUFFIX/$suffix/g" streets.combine.sql > "$filename.combine.sql"
		echo "Created SQL file: $filename.combine.sql"

		read -p "Execute script (y/n)? " answer
		if [[ $answer =~ ^[Yy]$ ]];
		then
			read -p "DB username: " user
			read -sp "DB password: " password
			echo ""
			echo "Executing script $filename.sql"
			mysql --user="$user" --password="$password" < $filename.sql
			echo "Created MySQL database: streets_$suffix"
			echo "Created MySQL table: streets_$suffix.WAYS"
			echo "Created MySQL table: streets_$suffix.SKIPPED_WAYS"
			echo "Created MySQL table: streets_$suffix.NODES"
			echo "Created MySQL table: streets_$suffix.NODE_MAP"
			echo "Cleaned streets_$suffix.NODE_MAP of unused nodes"
			echo "Skipped cleaning streets_$suffix.NODES of unused nodes, takes too long"

			read -p "Generate polylines now (y/n)? " answer
			if [[ $answer =~ ^[Yy]$ ]];
			then
				echo "Executing polyline generation script, this may take awhile..."
				python generate-polylines.py "$user" "$password" "streets_$suffix"

				echo -n "Combining ways into streets..."
				mysql --user="$user" --password="$password" < $filename.combine.sql				
				echo "Ways combined into streets"

				read -p "Set numeric street levels (y/n)? " answer
				if [[ $answer =~ ^[Yy]$ ]];
				then
					python street-levels.py "$user" "$password" "streets_$suffix"
				fi

				read -p "Fill in missing name bases now (y/n)? " answer
				if [[ $answer =~ ^[Yy]$ ]];
				then
					python add-name-bases.py "$user" "$password" "streets_$suffix"
				fi

			fi

			read -p "Delete generated files (y/n)? " answer
			if [[ $answer =~ ^[Yy]$ ]];
			then
				rm "$filename.nodes.xml" "$filename.ways.xml" "$filename.highways.xml" "$filename.nodes.tsv" "$filename.ways.tsv" "$filename.nodemap.tsv" "$filename.sql" "$filename.combine.sql"
			fi			
		fi			
	fi	

else
   echo "File $filename does not exist."
fi