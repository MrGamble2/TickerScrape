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

ticker_dict = { "name":[], \
                "symbol":[], \
                "postmentions":[], \
                "score":[]}
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
	ticker_dict["postmentions"].append(0)
	ticker_dict["score"].append(0)
reddit = praw.Reddit(client_id=cfg.redditconnection["clientid"], \
                     client_secret=cfg.redditconnection["clientsecret"], \
                     user_agent=cfg.redditconnection["useragent"], \
                     username=cfg.redditconnection["username"], \
                     password=cfg.redditconnection["password"])
#for sub_name in cfg.subreddits:  subreddit = reddit.subreddit("AskReddit")
#for submission in subreddit.stream.submissions()
#	sub = reddit.subreddit(sub_name)
#for submission in reddit.subreddit()
subreddit = reddit.subreddit("wallstreetbets")
for submission in subreddit.stream.submissions():
	for j in range(len(ticker_dict["symbol"])):
		if len(ticker_dict["symbol"][j])>1:
			if (find_only_whole_word(ticker_dict["symbol"][j], submission.title) 
			or find_only_whole_word("$"+ticker_dict["symbol"][j],submission.title)
			or find_only_whole_word(ticker_dict["symbol"][j], submission.selftext)
			or find_only_whole_word("$"+ticker_dict["symbol"][j], submission.selftext)
			or find_only_whole_word(ticker_dict["name"][j], submission.title)
			or find_only_whole_word(ticker_dict["name"][j], submission.selftext)):
				values = (ticker_dict["symbol"][j], "wallstreetbets", datetime.datetime.fromtimestamp(submission.created))
				sql = "INSERT INTO tickermention (ticker_name, sub_name, createdon) VALUES (%s, %s, %s)"
				dbcursor.execute(sql,values)
				print(values)
		else:
			if (find_only_whole_word("$"+ticker_dict["symbol"][j], submission.title)
			or find_only_whole_word("$"+ticker_dict["symbol"][j], submission.selftext)
			or find_only_whole_word(ticker_dict["name"][j], submission.title)
			or find_only_whole_word(ticker_dict["name"][j], submission.selftext)):
				values = (ticker_dict["symbol"][j], "wallstreetbets", datetime.datetime.fromtimestamp(submission.created))
				sql = "INSERT INTO tickermention (ticker_name, sub_name, createdon) VALUES (%s, %s, %s)"
				dbcursor.execute(sql,values)
				print(values)