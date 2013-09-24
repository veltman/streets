# Given an XML file with <ways>, prints a TSV, each row is: WAY_ID	NAME	NAME_BASE	NAME_TYPE	HIGHWAY_TYPE	XML_CONTENTS

from bs4 import BeautifulSoup
import sys

def IsHighwayAndHasName(way):
	"""Return True if the way passed in has a non-empty "highway" tag and a non-empty "name" tag
	"""
	hasName = isHighway = False
	for tag in way.find_all("tag"):
		if tag.has_attr("k") and tag["k"] == "highway" and tag.has_attr("v") and tag["v"]:
			isHighway = True
		elif tag.has_attr("k") and tag["k"] == "name" and tag.has_attr("v") and tag["v"]:
			hasName = True
	return (hasName and isHighway)

def escapeCell(cell):
	"""Escape trailing backslashes and tabs from each field to prevent problem with MySQL import
	"""
	return cell.strip().strip('\\').replace('\t',' ')

def escapeResult(result):
	"""Escape each cell in a row
	"""
	for key in result:
		result[key] = escapeCell(str(result[key]))
	return result

def PrintStreet(way):
	"""Print a street row in the following order:
	way_id name name_base name_type highway xml_contents
	"""	
	result = {"id": "", "name": "", "tiger:name_base": "", "tiger:name_type": "", "highway": "", "xml_contents": str(way).replace("\n","")}		
	
	#for nd in way.find_all("nd"):
	#	if nd.has_attr("ref"):
	#		result["nodes"].append(nd["ref"])
	if way.has_attr("id"):
		result["id"] = way["id"]

	for tag in way.find_all("tag"):
		if tag.has_attr("k") and tag.has_attr("v") and tag["k"] in result:
			result[tag["k"]] = tag["v"]

	result = escapeResult(result)

	row = result["id"]+"\t"+result["name"].strip()+"\t"+result["tiger:name_base"].strip()+"\t"+result["tiger:name_type"].strip()+"\t"+result["highway"].strip()+"\t"+result["xml_contents"]

	print row

	return 1

def GetStreets(osm):
	"""From the text of an OpenStreetMap extract, get the details for every <way> with the "highway" key set
	Prints all matching ways with tab delimiting in this order:
	id name name_base name_type highway contents
	"""
	soup = BeautifulSoup(osm,"xml")
	for way in soup.find_all("way"):		
		if IsHighwayAndHasName(way):
			PrintStreet(way)
	return 1

if len(sys.argv) > 1:
	reload(sys)
	sys.setdefaultencoding('utf8')
	try:
		f = open(sys.argv[1],"r")
		osm = f.read()
		result = GetStreets(osm)		
	except IOError:
		print "File " + sys.argv[1] + " does not exist"			
	reload(sys)
else:
	print "Required arguments: [input xml file]"
	print "Example: python extract-ways.py chicago.osm"