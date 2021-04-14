#! python3
import praw
#import pandas as pd
import datetime as dt
import userconfig as cfg
import mysql.connector
import os, sys, re, itertools, datetime
import matplotlib.pyplot as plt
import numpy as np

dbconnection = mysql.connector.connect(
  host=cfg.dbconfig["host"],
  user=cfg.dbconfig["user"],
  password=cfg.dbconfig["password"],
  database=cfg.dbconfig["dbname"],
  autocommit=True
)
dbcursor = dbconnection.cursor()

#pi chart: Bring back all posts in the last x days linked-entity with mentions and make a pi chart
val = input("Enter your value: ")