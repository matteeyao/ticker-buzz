# -*- coding: utf-8 -*-
"""
Module doc string
"""
# SET CHDIR TO CURRENT DIR
import sys, os
# sys.path.insert(0, os.path.realpath(os.path.dirname(__file__)))
# os.chdir(os.path.realpath(os.path.dirname(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
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
from dotenv import load_dotenv

load_dotenv()

## PUT YOUR URL IN AN ENVIRONMENT VARIABLE AND CONNECT.
engine=create_engine(os.getenv("DATABASE_URL"))
mydb=scoped_session(sessionmaker(bind=engine))

company="Gamestop"
ticker="GME"

reddit_df = pd.read_sql(
                """SELECT * FROM reddit_data
                ORDER BY date_time DESC LIMIT 20;""", con=engine, params=('%'+company+'%', '%$'+ticker+' %',))

print(reddit_df)