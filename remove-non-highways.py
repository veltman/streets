# Loop through XML and selectively print, skipping <ways> that are not highways (landmarks, parks, etc.)

import sys
import re

if len(sys.argv) > 1:
	try:
		f = open(sys.argv[1],"r")		
				
		buffer = ''
		isHighway = False
		line = f.readline()
		while line != '':
			if re.match('^\s*[<].?(osm|xml)',line):
				print line

			elif re.match('^\s*[<]way[^>]+[^/][>]',line) :
				buffer = line

			elif re.match('^\s*[<]tag',line) and re.search('k[=]"highway"',line):				
				isHighway = True
				if len(buffer):
					buffer = buffer+line

			elif re.match('^\s*[<]/way',line):
				buffer = buffer+line
				if isHighway:
					print buffer
				buffer = ''
				isHighway = False

			else:
				if len(buffer):
					buffer = buffer+line

			line = f.readline()

	except IOError:
		print "File " + sys.argv[1] + " does not exist"			
else:
	print "Required arguments: [input xml file]"
	print "Example: python remove-non-highways.py chicago.osm"