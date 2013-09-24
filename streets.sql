DROP DATABASE IF EXISTS `streets_SUFFIX`;
CREATE DATABASE IF NOT EXISTS `streets_SUFFIX`;
USE `streets_SUFFIX`;

# Can't seem to get this to stick, let's try all three
SET GLOBAL group_concat_max_len=16777216;
SET group_concat_max_len=16777216;
SET SESSION group_concat_max_len=16777216;

# Create tables
CREATE TABLE IF NOT EXISTS `streets_SUFFIX`.`WAYS` (ID BIGINT NOT NULL PRIMARY KEY, NAME TEXT NOT NULL, NAME_BASE TEXT NOT NULL, NAME_TYPE TEXT NOT NULL, STREET_TYPE TEXT NOT NULL, CONTENTS TEXT NOT NULL, POLYLINE LONGTEXT NOT NULL, PROCESSED TINYINT(1) NOT NULL, SKIP TINYINT(1) NOT NULL);
CREATE TABLE IF NOT EXISTS `streets_SUFFIX`.`SKIPPED_WAYS` LIKE `streets_SUFFIX`.`WAYS`;
CREATE TABLE IF NOT EXISTS `streets_SUFFIX`.`NODES` (ID BIGINT NOT NULL PRIMARY KEY, LATITUDE TEXT NOT NULL,LONGITUDE TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS `streets_SUFFIX`.`NODE_MAP` (ID BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY, WAY_ID BIGINT NOT NULL,NODE_ID BIGINT NOT NULL,SEQUENCE INT NOT NULL);

# Populate tables
LOAD DATA INFILE 'ABSOLUTEPATHFILENAME.ways.tsv' INTO TABLE `streets_SUFFIX`.`WAYS` (ID, NAME, NAME_BASE, NAME_TYPE, STREET_TYPE, CONTENTS);
LOAD DATA INFILE 'ABSOLUTEPATHFILENAME.nodes.tsv' INTO TABLE `streets_SUFFIX`.`NODES` (ID, LATITUDE, LONGITUDE);
LOAD DATA INFILE 'ABSOLUTEPATHFILENAME.nodemap.tsv' INTO TABLE `streets_SUFFIX`.`NODE_MAP` (WAY_ID,NODE_ID,SEQUENCE);

# Some basic cleanup
# Fix suffix inconsistencies in OSM
UPDATE `streets_SUFFIX`.`WAYS` SET `NAME` =  CONCAT( LEFT( NAME, LENGTH( NAME ) -3 ) ,  ' Place' ) WHERE LOWER( NAME ) REGEXP  ' pl$';
UPDATE `streets_SUFFIX`.`WAYS` SET `NAME` =  CONCAT( LEFT( NAME, LENGTH( NAME ) -3 ) ,  ' Drive' ) WHERE LOWER( NAME ) REGEXP  ' dr$';
UPDATE `streets_SUFFIX`.`WAYS` SET `NAME` =  CONCAT( LEFT( NAME, LENGTH( NAME ) -3 ) ,  ' Court' ) WHERE LOWER( NAME ) REGEXP  ' ct$';
UPDATE `streets_SUFFIX`.`WAYS` SET `NAME` =  CONCAT( LEFT( NAME, LENGTH( NAME ) -3 ) ,  ' Street' ) WHERE LOWER( NAME ) REGEXP  ' st$';
UPDATE `streets_SUFFIX`.`WAYS` SET `NAME` =  CONCAT( LEFT( NAME, LENGTH( NAME ) -3 ) ,  ' Road' ) WHERE LOWER( NAME ) REGEXP  ' rd$';
UPDATE `streets_SUFFIX`.`WAYS` SET `NAME` =  CONCAT( LEFT( NAME, LENGTH( NAME ) -3 ) ,  ' Avenue' ) WHERE LOWER( NAME ) REGEXP  ' av$';
UPDATE `streets_SUFFIX`.`WAYS` SET `NAME` =  CONCAT( LEFT( NAME, LENGTH( NAME ) -3 ) ,  ' Lane' ) WHERE LOWER( NAME ) REGEXP  ' ln$';
UPDATE `streets_SUFFIX`.`WAYS` SET `NAME` =  CONCAT( LEFT( NAME, LENGTH( NAME ) -3 ) ,  ' Bridge' ) WHERE LOWER( NAME ) REGEXP  ' br$';
UPDATE `streets_SUFFIX`.`WAYS` SET `NAME` =  CONCAT( LEFT( NAME, LENGTH( NAME ) -4 ) ,  ' Street' ) WHERE LOWER( NAME ) REGEXP  ' str$';
UPDATE `streets_SUFFIX`.`WAYS` SET `NAME` =  CONCAT( LEFT( NAME, LENGTH( NAME ) -4 ) ,  ' Avenue' ) WHERE LOWER( NAME ) REGEXP  ' ave$';
UPDATE `streets_SUFFIX`.`WAYS` SET `NAME` =  CONCAT( LEFT( NAME, LENGTH( NAME ) -4 ) ,  ' Highway' ) WHERE LOWER( NAME ) REGEXP  ' hwy$';
UPDATE `streets_SUFFIX`.`WAYS` SET `NAME` =  CONCAT( LEFT( NAME, LENGTH( NAME ) -4 ) ,  ' Freeway' ) WHERE LOWER( NAME ) REGEXP  ' fwy$';
UPDATE `streets_SUFFIX`.`WAYS` SET `NAME` =  CONCAT( LEFT( NAME, LENGTH( NAME ) -5 ) ,  ' Boulevard' ) WHERE LOWER( NAME ) REGEXP  ' blvd$';
UPDATE `streets_SUFFIX`.`WAYS` SET `NAME` =  CONCAT( LEFT( NAME, LENGTH( NAME ) -4 ) ,  ' Place' ) WHERE LOWER( NAME ) REGEXP  ' pl[.]$';
UPDATE `streets_SUFFIX`.`WAYS` SET `NAME` =  CONCAT( LEFT( NAME, LENGTH( NAME ) -4 ) ,  ' Court' ) WHERE LOWER( NAME ) REGEXP  ' ct[.]$';
UPDATE `streets_SUFFIX`.`WAYS` SET `NAME` =  CONCAT( LEFT( NAME, LENGTH( NAME ) -4 ) ,  ' Drive' ) WHERE LOWER( NAME ) REGEXP  ' dr[.]$';
UPDATE `streets_SUFFIX`.`WAYS` SET `NAME` =  CONCAT( LEFT( NAME, LENGTH( NAME ) -4 ) ,  ' Street' ) WHERE LOWER( NAME ) REGEXP  ' st[.]$';
UPDATE `streets_SUFFIX`.`WAYS` SET `NAME` =  CONCAT( LEFT( NAME, LENGTH( NAME ) -4 ) ,  ' Road' ) WHERE LOWER( NAME ) REGEXP  ' rd[.]$';
UPDATE `streets_SUFFIX`.`WAYS` SET `NAME` =  CONCAT( LEFT( NAME, LENGTH( NAME ) -4 ) ,  ' Avenue' ) WHERE LOWER( NAME ) REGEXP  ' av[.]$';
UPDATE `streets_SUFFIX`.`WAYS` SET `NAME` =  CONCAT( LEFT( NAME, LENGTH( NAME ) -4 ) ,  ' Lane' ) WHERE LOWER( NAME ) REGEXP  ' ln[.]$';
UPDATE `streets_SUFFIX`.`WAYS` SET `NAME` =  CONCAT( LEFT( NAME, LENGTH( NAME ) -4 ) ,  ' Bridge' ) WHERE LOWER( NAME ) REGEXP  ' br[.]$';
UPDATE `streets_SUFFIX`.`WAYS` SET `NAME` =  CONCAT( LEFT( NAME, LENGTH( NAME ) -5 ) ,  ' Street' ) WHERE LOWER( NAME ) REGEXP  ' str[.]$';
UPDATE `streets_SUFFIX`.`WAYS` SET `NAME` =  CONCAT( LEFT( NAME, LENGTH( NAME ) -5 ) ,  ' Avenue' ) WHERE LOWER( NAME ) REGEXP  ' ave[.]$';
UPDATE `streets_SUFFIX`.`WAYS` SET `NAME` =  CONCAT( LEFT( NAME, LENGTH( NAME ) -5 ) ,  ' Highway' ) WHERE LOWER( NAME ) REGEXP  ' hwy[.]$';
UPDATE `streets_SUFFIX`.`WAYS` SET `NAME` =  CONCAT( LEFT( NAME, LENGTH( NAME ) -5 ) ,  ' Freeway' ) WHERE LOWER( NAME ) REGEXP  ' fwy[.]$';
UPDATE `streets_SUFFIX`.`WAYS` SET `NAME` =  CONCAT( LEFT( NAME, LENGTH( NAME ) -6 ) ,  ' Boulevard' ) WHERE LOWER( NAME ) REGEXP  ' blvd[.]$';

# Take out alleys and footpaths and numerical streets
UPDATE `streets_SUFFIX`.`WAYS` SET `NAME` = TRIM(`NAME`);
UPDATE `streets_SUFFIX`.`WAYS` SET `SKIP` = 1 WHERE TRIM(LOWER(`STREET_TYPE`)) NOT IN ('motorway','motorway_link','trunk','trunk_link','primary','primary_link','secondary','secondary_link','tertiary','tertiary_link','residential','living_street','road') OR `NAME` REGEXP '^((northeast|northwest|southeast|southwest|east|north|south|west|ne[.]?|nw[.]?|se[.]?|sw[.]?|e[.]?|n[.]?|s[.]?|w[.]?) +)?[0-9]+';
INSERT INTO `streets_SUFFIX`.`SKIPPED_WAYS` SELECT * FROM `streets_SUFFIX`.`WAYS` WHERE `SKIP` = 1;
DELETE FROM `streets_SUFFIX`.`NODE_MAP` WHERE `WAY_ID` IN (SELECT ID FROM `streets_SUFFIX`.`SKIPPED_WAYS`);
DELETE FROM `streets_SUFFIX`.`WAYS` WHERE `SKIP` = 1;

GRANT SELECT ON `streets_SUFFIX`.* TO 'streets'@'localhost';