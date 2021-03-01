#! python3
import praw
#import pandas as pd
import datetime as dt
import userconfig as cfg
import mysql.connector
import os, sys, re, itertools, datetime

#connect to reddit
reddit = praw.Reddit(client_id=cfg.redditconnection["clientid"], \
                     client_secret=cfg.redditconnection["clientsecret"], \
                     user_agent=cfg.redditconnection["useragent"], \
                     username=cfg.redditconnection["username"], \
                     password=cfg.redditconnection["password"])
#connect to db and get ticker mentions from last 24 hrs
dbconnection = mysql.connector.connect(
  host=cfg.dbconfig["host"],
  user=cfg.dbconfig["user"],
  password=cfg.dbconfig["password"],
  database=cfg.dbconfig["dbname"]
)
dbcursor = dbconnection.cursor()
dbcursor.execute("SELECT * FROM post WHERE postdate >= now() - INTERVAL 2 DAY")
result = dbcursor.fetchall()

#for each ticker get from praw and update score
for post in result:
	#id is stored in 0
	submission = reddit.submission(id=post[0])
	sql = "UPDATE post SET score = "+ str(submission.score) +" WHERE reddit_id = '"+ post[0]+"'"
	print(sql)
	dbcursor.execute(sql)
	dbconnection.commit()