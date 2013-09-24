#After an OSM file is extracted to MySQL, try to correct inconsitent name bases

import sys
import time
import math
import re
import MySQLdb

def ExtractNameBase(name):	
	"""Get the expected name base for a street name
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

	return re.sub(' (Street|Drive|Way|Lane|Road|Freeway|Highway|Expressway|Alley|Terrace|Court|Boulevard|Avenue|Place|Skyway|Parkway|Square|Plaza|Park|Bridge|Crescent|Pike|Mall|Tollway|Circle|Loop|Walk|St|Dr|Ln|Rd|Fwy|Expy|Hwy|Ter|Ct|Blvd|Ave|Pl|Pky|Pkwy|Sq|Br|Tunnel|Row|Gardens|Trail)$','',name)

if len(sys.argv) < 4:
	print "Invalid syntax, need DB user, DB password, and DB name"
else:
	db_user = sys.argv[1]
	db_password = sys.argv[2]
	db_name = sys.argv[3]
	db = MySQLdb.connect(host="localhost", user=db_user, passwd=db_password, db=db_name)	
	cur = db.cursor()
	update_cur = db.cursor()

	cur.execute("SELECT `ITEM_ID`,TRIM(`NAME`),`NAME_BASE` FROM `" + db_name + "`.`STREET_DETAILS` WHERE `NAME_BASE` != '' AND SKIP = 0 ORDER BY RAND()")

	to_fix = []

	rowcount = cur.rowcount

	for i in range(rowcount):		

		row = cur.fetchone()

		# Compare calculated name base against the name base currently in the DB, prompt for corrections
		if ExtractNameBase(row[1]) != row[2]:
			print "("+str(i+1)+"/"+str(rowcount)+") Base for "+row[1]+" is ["+row[2]+"], expected ("+ExtractNameBase(row[1])+")"
			new_base = raw_input("New name base, or hit enter to skip: ")
			if len(new_base.strip()):
				street_id = str(row[0])
				new_base = new_base.strip()
				update_cur.execute("UPDATE `"+db_name+"`.`STREET_DETAILS` SET `NAME_BASE`=%s WHERE `ITEM_ID`=%s",(new_base,street_id))
				db.commit()
				print "Updated to "+new_base
			else:
				print "Skipped"
			print ""