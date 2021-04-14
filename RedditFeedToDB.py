#! python3
import praw
#import pandas as pd
import datetime as dt
import userconfig as cfg
import mysql.connector
import os, sys, re, itertools, datetime

def find_only_whole_word(search_string, input_string):
	# Create a raw string with word boundaries from the user's input_string
	raw_search_string = r"\b" + search_string + r"\b"

	try:
		match_output = re.search(raw_search_string, input_string)
		no_match_was_found = ( match_output is None )
		if no_match_was_found:
			return False
		else:
			return True
	except:
		return False
def execute_sql(cursor, sql, values):
	try:
		cursor.execute(sql,values)
	except Exception as inst:
		print(inst)

ticker_dict = { "name":[], \
                "symbol":[], \
                "postmentions":[], \
                "score":[],\
                "strict":[]}
#replace with a database query 3306
dbconnection = mysql.connector.connect(
  host=cfg.dbconfig["host"],
  user=cfg.dbconfig["user"],
  password=cfg.dbconfig["password"],
  database=cfg.dbconfig["dbname"],
  autocommit=True
)
dbcursor = dbconnection.cursor()
dbcursor.execute("SELECT * FROM tickers")
result = dbcursor.fetchall()
for ticker in result:
	ticker_dict["symbol"].append(ticker[0])
	ticker_dict["name"].append(ticker[1])
	ticker_dict["strict"].append(ticker[2])
	ticker_dict["postmentions"].append(0)
	ticker_dict["score"].append(0)

reddit = praw.Reddit(client_id=cfg.redditconnection["clientid"], \
                     client_secret=cfg.redditconnection["clientsecret"], \
                     user_agent=cfg.redditconnection["useragent"], \
                     username=cfg.redditconnection["username"], \
                     password=cfg.redditconnection["password"])
#Watch submissions
subreddit = reddit.subreddit("wallstreetbets")
for submission in subreddit.stream.submissions():
	added = False
	for j in range(len(ticker_dict["symbol"])):
		if len(ticker_dict["symbol"][j])>1 & ticker_dict["strict"][j] == 0:
			if (find_only_whole_word(ticker_dict["symbol"][j], submission.title) 
			or find_only_whole_word("$"+ticker_dict["symbol"][j],submission.title)
			or find_only_whole_word(ticker_dict["symbol"][j], submission.selftext)
			or find_only_whole_word("$"+ticker_dict["symbol"][j], submission.selftext)
			or find_only_whole_word(ticker_dict["name"][j], submission.title)
			or find_only_whole_word(ticker_dict["name"][j], submission.selftext)):
				if not added:
					values = (submission.id, "wallstreetbets", datetime.datetime.fromtimestamp(submission.created), submission.url, submission.score)
					sql = "INSERT INTO post (reddit_id, sub_name, postdate, url, score) VALUES (%s, %s, %s, %s, %s)"
					execute_sql(dbcursor,sql,values)
				values = (ticker_dict["symbol"][j], submission.id)
				sql = "INSERT INTO tickermention (ticker_name, reddit_id) VALUES (%s, %s)"
				execute_sql(dbcursor,sql,values)
				added = True
				print(values)
		else:
			if (find_only_whole_word("$"+ticker_dict["symbol"][j], submission.title)
			or find_only_whole_word("$"+ticker_dict["symbol"][j], submission.selftext)
			or find_only_whole_word(ticker_dict["name"][j], submission.title)
			or find_only_whole_word(ticker_dict["name"][j], submission.selftext)):
				if not added:
					values = (submission.id, "wallstreetbets", datetime.datetime.fromtimestamp(submission.created), submission.url, submission.score)
					sql = "INSERT INTO post (reddit_id, sub_name, postdate, url, score) VALUES (%s, %s, %s, %s, %s)"
					execute_sql(dbcursor,sql,values)
				values = (ticker_dict["symbol"][j], submission.id)
				sql = "INSERT INTO tickermention (ticker_name, reddit_id) VALUES (%s, %s)"
				dbcursor.execute(sql,values)
				added = True
				print(values)