#! python3
import praw
#import pandas as pd
import datetime as dt
import userconfig as cfg
import os, sys, re, itertools

def find_only_whole_word(search_string, input_string):
  # Create a raw string with word boundaries from the user's input_string
  raw_search_string = r"\b" + search_string + r"\b"

  match_output = re.search(raw_search_string, input_string, flags=re.IGNORECASE)

  no_match_was_found = ( match_output is None )
  if no_match_was_found:
    return False
  else:
    return True

ticker_dict = { "name":[], \
                "symbol":[], \
                "postmentions":[], \
                "score"}      

#replace with a database query 3306
directory = os.listdir('Exchanges')
for x in directory:
	path = 'Exchanges/' + x
	#with open(path, 'r') as fp
	try:
		fp = open(path,'r')
		line = fp.readline()
		while line:
			values = line.split("\t")
			ticker_dict["symbol"].append(values[0])
			ticker_dict["name"].append(values[1])
			ticker_dict["postmentions"].append(0)
			ticker_dict["score"].append(0)
			line = fp.readline();
	except:
    	print("Unexpected error:", sys.exc_info()[0])
	finally:
		fp.close()

reddit = praw.Reddit(client_id=cfg.redditconnection["clientid"], \
                     client_secret=cfg.redditconnection["clientsecret"], \
                     user_agent=cfg.redditconnection["useragent"], \
                     username=cfg.redditconnection["username"], \
                     password=cfg.redditconnection["password"])
for submission in reddit.subre