# Given an XML file with <nodes>, prints a TSV, each row is:	NODE_ID	LATITUDE	LONGITUDE

from bs4 import BeautifulSoup
import sys

def escapeCell(cell):
	"""Escape trailing backslashes and tabs from each field to prevent problem with MySQL import
	"""
	return cell.strip().strip('\\').replace('\t',' ')

def GetNodes(osm):
	"""From the text of an OpenStreetMap extract, get the ID and lat/lng of each node
	Prints all nodes with tab delimiting in this order:
	node_id latitude longitude
	"""
	soup = BeautifulSoup(osm,"xml")
	for node in soup.find_all('node'):		
		if node.has_attr("id") & node.has_attr("lat") & node.has_attr("lon"):
			print escapeCell(str(node["id"]))+"\t"+escapeCell(str(node["lat"]))+"\t"+escapeCell(str(node["lon"]))
	return 1

if len(sys.argv) > 1:
	try:
		f = open(sys.argv[1],"r")
		osm = f.read()
		result = GetNodes(osm)
	except IOError:
		print "File " + sys.argv[1] + " does not exist"			
else:
	print "Required arguments: [input xml file]"
	print "Example: python extract.py chicago.osm"