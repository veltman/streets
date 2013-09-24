# Given an XML file with <ways>, prints a TSV, each row is: WAY_ID	NODE_ID	NUM_IN_SEQUENCE

from bs4 import BeautifulSoup
import sys

def escapeCell(cell):
	"""Escape trailing backslashes and tabs from each field to prevent problem with MySQL import
	"""
	return cell.strip().strip('\\').replace('\t',' ')

def GetNodeMap(osm):
	"""From the text of an OpenStreetMap extract, get the ID and lat/lng of each node

	Prints all nodes with tab delimiting"""
	soup = BeautifulSoup(osm,"xml")		
	for way in soup.find_all("way"):
		i = 0	
		isHighway = False	

		for tag in way.find_all("tag"):
			if tag.has_attr("k") and tag["k"] == "highway":
				isHighway = True
				break

		if isHighway:
			for nd in way.find_all("nd"):
				if nd.has_attr("ref"):
					print escapeCell(str(way["id"]))+"\t"+escapeCell(str(nd["ref"]))+"\t"+escapeCell(str(i))
					i = i+1
	return 1

if len(sys.argv) > 1:
	try:
		f = open(sys.argv[1],"r")
		osm = f.read()
		result = GetNodeMap(osm)
	except IOError:
		print "File " + sys.argv[1] + " does not exist"			
else:
	print "Required arguments: [input xml file]"
	print "Example: python extract-node-map.py chicago.osm"