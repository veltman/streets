import sys
import time
import math
import MySQLdb

def StreetLevelFromStreetTypes(street_types):
	# return numeric value, 1 for highway, 5 for tiny alley
	types = street_types.split(",")
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

if len(sys.argv) < 4:
	print "Invalid syntax, need DB user, DB password, and DB name"
else:
	db_user = sys.argv[1]
	db_password = sys.argv[2]
	db_name = sys.argv[3]
	db = MySQLdb.connect(host="localhost", user=db_user, passwd=db_password, db=db_name)	
	cur = db.cursor()
	update_cur = db.cursor()

	cur.execute("SELECT `ITEM_ID`,`STREET_TYPE` FROM `" + db_name + "`.`STREET_DETAILS`")

	print str(cur.rowcount)+" streets to be processed"

	rowcount = cur.rowcount
	start_time = time.time()
	for i in range(rowcount):
		
		row = cur.fetchone()
		street_id = str(row[0])
		#print row[1]
		street_level = str(StreetLevelFromStreetTypes(row[1]))
		
		update_cur.execute("UPDATE `"+db_name+"`.`STREET_DETAILS` SET `STREET_LEVEL`=%s WHERE `ITEM_ID`=%s",(street_level,street_id))
		db.commit()
		execution_time = round(time.time()-start_time)
		print "("+str(i+1)+"/"+str(rowcount)+") ["+str(int(math.floor(execution_time / 60)))+":"+str(int(execution_time % 60))+"] "+"UPDATE `"+db_name+"`.`STREET_DETAILS` SET `STREET_LEVEL`="+street_level+" WHERE `ITEM_ID`="+street_id