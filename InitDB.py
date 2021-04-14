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
dbcursor.execute("CREATE TABLE globalconfig (name VARCHAR(255), value VARCHAR(255))")
print("1")
dbcursor.execute("CREATE TABLE tickers (ticker VARCHAR(255) NOT NULL, full_name VARCHAR(255), strict_mentions Boolean, PRIMARY KEY (ticker))")
print("2")
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
	#loop through exchanges and add tickers to db
	try:
		fp = open(path,'r')
		line = fp.readline()
		while line:
			values = line.rstrip().split("\t")
			values.append(False)
			sql = "INSERT INTO tickers (ticker, full_name, strict_mentions) VALUES (%s, %s, %s)"
			try:
				dbcursor.execute(sql,values)
			except Exception as inst:
				print(inst)
				print("values:", values )
				
			line = fp.readline();
	except:
		print("Unexpected file error:", sys.exc_info()[0])
	finally:
		fp.close()

#import stricter mentions of a ticker
print("4")
try:
	fp = open('StrictMentions.txt','r')
	line = fp.readline()
	while line:
		print(line)
		try:
			value = line.rstrip()
			print(value)
			sql = "UPDATE tickers SET strict_mentions = True WHERE ticker = '" + value + "'"
			print(sql)
			dbcursor.execute(sql)
		except Exception as inst:
			print(inst)
		line = fp.readline()
except Exception as inst:
	print(inst)


for sub in cfg.subreddits:
	values = (sub,)
	sql = "INSERT INTO subreddits (name) VALUES (%s)"
	dbcursor.execute(sql,values)
