#After an OSM file is extracted to MySQL, try to fill in missing name bases


import sys
import time
import math
import re
import MySQLdb

def ExtractNameBase(name):	
	"""Attempt to get the name base by dropping common prefixes and suffixes
	"""
	name = re.sub('[.]$','',name)

	if not re.match('^[A-Za-z0-9 ]+$',name):
		return ''

	name = re.sub('^[NSEWnsew]{1,2}[.]? ','',name)
	name = re.sub(' [NSEWnsew]{1,2}[.]?$','',name)
	name = re.sub('^(North|South|East|West|Northwest|Northeast|Southwest|Southeast) ','',name)
	name = re.sub(' (North|South|East|West|Northwest|Northeast|Southwest|Southeast)$','',name)
	name = re.sub('^(Upper|Lower) ','',name)
	name = re.sub('^The ','',name)

	if not re.search(' (Street|Drive|Way|Lane|Road|Freeway|Highway|Expressway|Alley|Terrace|Court|Boulevard|Avenue|Place|Skyway|Parkway|Square|Plaza|Park|Bridge|Tollway|Circle|Loop|St|Dr|Ln|Rd|Fwy|Expy|Hwy|Ter|Ct|Blvd|Ave|Pl|Pky|Pkwy|Sq|Br|Tunnel|Row|Gardens|Trail)$',name):
		return ''

	return re.sub(' (Street|Drive|Way|Lane|Road|Freeway|Highway|Expressway|Alley|Terrace|Court|Boulevard|Avenue|Place|Skyway|Parkway|Square|Plaza|Park|Bridge|Tollway|Circle|Loop|St|Dr|Ln|Rd|Fwy|Expy|Hwy|Ter|Ct|Blvd|Ave|Pl|Pky|Pkwy|Sq|Br|Tunnel|Row|Gardens|Trail)$','',name)

if len(sys.argv) < 4:
	print "Invalid syntax, need DB user, DB password, and DB name"
else:
	db_user = sys.argv[1]
	db_password = sys.argv[2]
	db_name = sys.argv[3]
	db = MySQLdb.connect(host="localhost", user=db_user, passwd=db_password, db=db_name)	
	cur = db.cursor()
	update_cur = db.cursor()

	cur.execute("SELECT `ITEM_ID`,TRIM(`NAME`) FROM `" + db_name + "`.`STREET_DETAILS` WHERE TRIM(`NAME_BASE`) = ''")

	print str(cur.rowcount)+" streets with no name base"

	rowcount = cur.rowcount
	start_time = time.time()
	for i in range(rowcount):
		
		row = cur.fetchone()
		street_id = str(row[0])

		street_name = str(row[1])

		new_base = ExtractNameBase(street_name);
				
		update_cur.execute("UPDATE `"+db_name+"`.`STREET_DETAILS` SET `NAME_BASE`=%s WHERE `ITEM_ID`=%s",(new_base,street_id))
		db.commit()
		execution_time = round(time.time()-start_time)		
		if len(new_base) == 0:
			print "("+str(i+1)+"/"+str(rowcount)+") ["+str(int(math.floor(execution_time / 60)))+":"+str(int(execution_time % 60))+"] "+"Could not compute name base for "+street_name