# -*- coding: utf-8 -*-
"""
Module doc string
"""
import mysql.connector
from cachetools import LRUCache, cached, TTLCache
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from stockstats import StockDataFrame as Sdf
import dash_bootstrap_components as dbc
import dash_table as dt
import yahoo_fin.stock_info as yf
import yfinance
from datetime import datetime, timedelta, date
import plotly.graph_objs as go
import pickle
import numpy as np
import pandas as pd
import random
import numpy

## CONNECTING TO MYSQL
mydb = mysql.connector.connect(
    host="localhost",
    user="mattyyao",
    passwd="C02C75KSMD6R"
)

ticker = 'DIS'

reddit_df = pd.read_sql(
    """SELECT * FROM reddit_data.reddit_data_sentiment 
    WHERE body LIKE %s AND date_time > ADDDATE(date_time, -1)
    ORDER BY date_time DESC LIMIT 20;""", con=mydb, params=('%'+ticker+'%',))

reddit_df = reddit_df[['subreddit','date_time','body']]

print(reddit_df.values.tolist())