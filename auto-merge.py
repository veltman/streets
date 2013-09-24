# Merge streets with the same name

import sys
import time
import math
import re
import json
import MySQLdb

def StreetLevelFromStreetTypes(types):
	'''Return numeric value for a street street_level

	1 for highway, 5 for tiny alley
	'''
	values = {
        'unclassified': 5, \
        'road': 5, \
        'residential': 5, \
        'pedestrian': 5, \
        'living_street': 5, \
        'tertiary_link': 4, \
        'tertiary': 4, \
        'secondary_link': 3, \
        'secondary': 3, \
        'primary_link': 2, \
        'primary': 2, \
        'trunk_link': 1, \
        'trunk': 1, \
        'motorway_link': 1, \
        'motorway': 1
    	}

	if len(types) == 0:
		return 0
	elif len(types) == 1:
		if values[types[0]]:
			return values[types[0]]
		else:
			return 5

	counts = [0,0,0,0,0,0]

	for t in types:
		if t not in values:
			val = 0
		else:
			val = values[t]

		counts[val] = counts[val]+1

	max = 0
	mode = 5
	for i in range(6):
		if counts[i] != 0 and counts[i] >= max:
			max = counts[i]
			mode = i

	return mode

def MergePolylines(p1,p2):
	'''Merge two polylines/multipolylines into a single multipolyline
	'''
	if re.match('^\[\[\[.+\]\]\]$',p1):		
		p1 = p1[1:][:-1]
	if re.match('^\[\[\[.+\]\]\]$',p2):
		p2 = p2[1:][:-1]

	return "[" + p1 + "," + p2 + "]"


def DoMerge(master,others):
	'''Merge all streets in others into master
	'''
	way_ids = master[1].split(",")
	num_ways = master[2]
	polyline = master[3]
	street_types = master[4].split(",")	
	street_level = master[5]
	dimensions = master[6]	

	for o in others:
		street_types = street_types + o[4].split(",")
		num_ways = num_ways + o[2]
		way_ids = way_ids + o[1].split(",")
		polyline = MergePolylines(polyline,o[3])
		dimensions = 3

	street_level = StreetLevelFromStreetTypes(street_types)	

	return {"way_ids": way_ids, "num_ways": num_ways, "street_types": street_types, "street_level": street_level, "dimensions": dimensions, "polyline": polyline}

if len(sys.argv) < 4:
	print "Invalid syntax, need DB user, DB password, and DB name"
else:
	db_user = sys.argv[1]
	db_password = sys.argv[2]
	db_name = sys.argv[3]
	db = MySQLdb.connect(host="localhost", user=db_user, passwd=db_password, db=db_name)	
	cur = db.cursor()
	check_cur = db.cursor()
	update_cur = db.cursor()

	cur.execute("SELECT GROUP_CONCAT(`ID`),NAME FROM `" + db_name + "`.`ITEMS` WHERE SKIP = 0 GROUP BY NAME HAVING COUNT(*) > 1 ORDER BY NAME ASC")

	print str(cur.rowcount)+" exact duplicate groups"

	rowcount = cur.rowcount
	start_time = time.time()
	for i in range(rowcount):
		
		row = cur.fetchone()

		ids = row[0]

		print ids

		name = row[1]

		print name

		check_cur.execute("SELECT * FROM `" + db_name + "`.`HISTORY_MAP` WHERE `ITEM_ID` IN (" + ids + ")")
		
		if check_cur.rowcount > 0:
			print "Couldn't merge " + name + ", histories already exist"
			continue

		check_cur.execute("SELECT d.ITEM_ID,d.WAY_IDS,d.NUM_WAYS,g.GEOMETRY,d.STREET_TYPE,d.STREET_LEVEL,g.DIMENSIONS,d.NAME FROM `" + db_name + "`.`STREET_DETAILS` d, GEOMETRIES g WHERE d.ITEM_ID = g.ITEM_ID AND d.ITEM_ID IN (" + ids + ") ORDER BY d.NUM_WAYS DESC, d.STREET_LEVEL ASC")
		
		others = []

		for j in range(check_cur.rowcount):
			if j == 0:
				master = check_cur.fetchone()				
			else:
				others.append(check_cur.fetchone())

		merged = DoMerge(master,others)

		skips = []

		for o in others:
			skips.append(str(o[0]))

		to_update = str(master[0])
		to_skip = ",".join(skips)

		print "updating "+to_update

		print "skipping "+to_skip		

		update_cur.execute("UPDATE ITEMS SET SKIP = 1 WHERE ID IN (%s)",(to_skip))
		db.commit()

		
		update_cur.execute("UPDATE STREET_DETAILS SET WAY_IDS = %s , NUM_WAYS = %s , STREET_TYPE = %s , STREET_LEVEL = %s , POLYLINE = %s WHERE ITEM_ID = %s",(",".join(merged["way_ids"]),str(merged["num_ways"]),",".join(merged["street_types"]),str(merged["street_level"]),merged["polyline"],to_update))
		db.commit()

		update_cur.execute("UPDATE GEOMETRIES SET DIMENSIONS = 3 , GEOMETRY = %s WHERE ITEM_ID = %s",(merged["polyline"],to_update))
		db.commit()