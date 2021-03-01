#! python3
import userconfig as cfg
import mysql.connector
import os, sys, re, itertools

dbconnection = mysql.connector.connect(
  host=cfg.dbconfig["host"],
  user=cfg.dbconfig["user"],
  password=cfg.dbconfig["password"]
)

#extend to check for db 
dbcursor = dbconnection.cursor()
sql = "CREATE DATABASE IF NOT EXISTS " + cfg.dbconfig["dbname"]
dbcursor.execute(sql)

dbconnection = mysql.connector.connect(
  host=cfg.dbconfig["host"],
  user=cfg.dbconfig["user"],
  password=cfg.dbconfig["password"],
  database=cfg.dbconfig["dbname"],
  autocommit=True
)
dbcursor = dbconnection.cursor()
#do we need every instance? Keep relationship simple (maybe have a calculated rollup field of amount?)
#then have an n:1 with a list of mentions, the mentions also point to a post? I mean we are only interested in
#counts so meh can have an expandable global config
dbcursor.execute("CREATE TABLE globalconfig (name VARCHAR(255), value VARCHAR(255))")
dbcursor.execute("CREATE TABLE tickers (ticker VARCHAR(255) NOT NULL, full_name VARCHAR(255), PRIMARY KEY (ticker))")
dbcursor.execute("CREATE TABLE subreddits (name VARCHAR(255) NOT NULL, PRIMARY KEY (name))")
dbcursor.execute("CREATE TABLE post (reddit_id VARCHAR(255) NOT NULL, sub_name VARCHAR(255),\
	postdate Datetime, url VARCHAR(255), score INT, PRIMARY KEY (reddit_id))")
#Was thinking about denomalizing dates but eh well see. 
dbcursor.execute("CREATE TABLE tickermention (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, \
	ticker_name VARCHAR(255),  reddit_id VARCHAR(255))")

#fill tickers and subs
directory = os.listdir('Exchanges')
for x in directory:
	path = 'Exchanges/' + x
	#with open(path, 'r') as fp
	try:
		fp = open(path,'r')
		line = fp.readline()
		while line:
			values = line.rstrip().split("\t")
			sql = "INSERT INTO tickers (ticker, full_name) VALUES (%s, %s)"
			try:
				dbcursor.execute(sql,values)
			except:
				print("error adding values ikely an issue with duplicate rows:" )
				print(values)
			line = fp.readline();
	except:
		print("Unexpected file error:", sys.exc_info()[0])
	finally:
		fp.close()
for sub in cfg.subreddits:
	values = (sub,)
	sql = "INSERT INTO subreddits (name) VALUES (%s)"
	dbcursor.execute(sql,values)

#thoughts on current design. One issue is if there are multiple mentions 
#in one post subsequent updates can be split so the score isnt the same. 
#and until we get a solid clearing (req $ list) of bad values. Keep ticker mention
#mostly the same, remove score instead have that in the post table