# -*- coding: utf-8 -*-
"""
Module doc string
"""
import dash
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

stock = yfinance.Ticker("TSLA")

print(stock.info['longName'])

