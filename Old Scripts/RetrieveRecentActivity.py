#! python3
#inital test for many concepts of praw and sorting. file will be deleted when split out eventually
import praw
import datetime as dt
import userconfig as cfg
import os, sys, re, itertools
#defs
def find_only_whole_word(search_string, input_string):
  # Create a raw string with word boundaries from the user's input_string
  raw_search_string = r"\b" + search_string + r"\b"

  match_output = re.search(raw_search_string, input_string, flags=re.IGNORECASE)

  no_match_was_found = ( match_output is None )
  if no_match_was_found:
    return False
  else:
    return True
#dict objects    
post_dict = { "title":[], \
                "score":[], \
                "id":[], "url":[], \
                "comms_num": [], \
                "created": [], \
                "body":[]}

ticker_dict = { "name":[], \
                "symbol":[], \
                "postmentions":[], \
                "score":[]}            
#start    
reddit = praw.Reddit(client_id=cfg.redditconnection["clientid"], \
                     client_secret=cfg.redditconnection["clientsecret"], \
                     user_agent=cfg.redditconnection["useragent"], \
                     username=cfg.redditconnection["username"], \
                     password=cfg.redditconnection["password"])

#possibly make this a config?
subreddit = reddit.subreddit('Wallstreetbets')
subreddit_new = subreddit.new(limit=1000)
for post in subreddit_new:
	post_dict["title"].append(post.title)
	post_dict["score"].append(post.score)
	post_dict["id"].append(post.id)
	post_dict["url"].append(post.url)
	post_dict["comms_num"].append(post.num_comments)
	post_dict["created"].append(post.created)
	post_dict["body"].append(post.selftext)
#we need to get all tickers in the Exchanges folder (downloaded from http://www.eoddata.com/symbols.aspx)
#Would be nice to find a json or possibly even a py that does this for us already 
#the ticker and the name are deliniated by a tab while the each stock is seperated by a line. 
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

for i in range(len(post_dict["title"])):
	#TODO: Improve regex so that we dont have to search multiple times, just one sweep for ex. $MSFT and MSFT. Should I multi thread this? I mean limit is 1000 and its
	#fine now but if I expand to do more stuff it might be worth multthreading.
	for j in range(len(ticker_dict["symbol"])):
		if len(ticker_dict["symbol"][j])>1:
			if (find_only_whole_word(ticker_dict["symbol"][j], post_dict["title"][i]) 
			or find_only_whole_word("$"+ticker_dict["symbol"][j], post_dict["title"][i])
			or find_only_whole_word(ticker_dict["symbol"][j], post_dict["body"][i])
			or find_only_whole_word("$"+ticker_dict["symbol"][j], post_dict["body"][i])):
				ticker_dict["postmentions"][j]+=1
				ticker_dict["score"][j]+=post_dict["score"][i]
		else:
			if (find_only_whole_word("$"+ticker_dict["symbol"][j], post_dict["title"][i])
			or find_only_whole_word("$"+ticker_dict["symbol"][j], post_dict["body"][i])):
				ticker_dict["postmentions"][j]+=1
				ticker_dict["score"][j]+=post_dict["score"][i]

sorted_ticker = sorted(zip(ticker_dict["name"], ticker_dict["symbol"], ticker_dict["postmentions"]), reverse=True, key=lambda x: x[2])
ticker_dict["name"], ticker_dict["symbol"], ticker_dict["postmentions"] = [[x[i] for x in sorted_ticker] for i in range(3)]
total = 0
for k in range(len(ticker_dict["symbol"])):
	if(ticker_dict["postmentions"][k]>0):
		total+=1
		print(ticker_dict["symbol"][k])
		print(ticker_dict["postmentions"][k])
		print(ticker_dict["score"][k])
print("total: "+str(total))

