# Generate polylines for each way based on the node map

import sys
import time
import math
import MySQLdb

if len(sys.argv) < 4:
	print "Invalid syntax, need DB user, DB password, and DB name"
else:
	db_user = sys.argv[1]
	db_password = sys.argv[2]
	db_name = sys.argv[3]
	db = MySQLdb.connect(host="localhost", user=db_user, passwd=db_password, db=db_name)	
	cur = db.cursor()
	poly_cur = db.cursor()

	cur.execute("SELECT `ID` FROM `" + db_name + "`.`WAYS` WHERE `PROCESSED` = 0")

	print str(cur.rowcount)+" ways to be processed"

	rowcount = cur.rowcount
	start_time = time.time()
	for i in range(rowcount):
		row = cur.fetchone()
		way_id = str(row[0]);	
		poly_cur.execute("SELECT CONCAT('[',GROUP_CONCAT(CONCAT('[',n.`LATITUDE`,',',n.`LONGITUDE`,']') ORDER BY m.SEQUENCE ASC),']') FROM `WAYS` w, `NODE_MAP` m, `NODES` n WHERE w.`ID` = "+way_id+" AND m.`NODE_ID` = n.`ID` AND m.`WAY_ID` = w.`ID` GROUP BY w.`ID` ORDER BY m.`SEQUENCE` ASC")
		poly_row = poly_cur.fetchone()		
		poly_cur.execute("UPDATE `WAYS` SET `POLYLINE`=%s,`PROCESSED`=%s WHERE `ID`=%s",(poly_row[0],"1",way_id))	
		db.commit()
		execution_time = round(time.time()-start_time)
		print "("+str(i+1)+"/"+str(rowcount)+") ["+str(int(math.floor(execution_time / 60)))+":"+str(int(execution_time % 60))+"] "+"UPDATE `WAYS` SET `POLYLINE` = '"+poly_row[0]+"', PROCESSED = 1 WHERE `ID` = "+way_id

	new_cur = db.cursor()

	new_cur.execute("SELECT `ID` FROM `"+ db_name +"`.`WAYS` WHERE `PROCESSED` = 0 OR `POLYLINE` NOT LIKE '[[%' OR `POLYLINE` NOT LIKE '%]]'")
	if new_cur.rowcount > 0:
		print "The following way IDs have a problem:"
		for i in range(new_cur.rowcount):
			print str(row[0])