# -*- coding: utf-8 -*-
"""
Module doc string
"""
# SET CHDIR TO CURRENT DIR
import os
import sys
# sys.path.insert(0, os.path.realpath(os.path.dirname(__file__)))
# os.chdir(os.path.realpath(os.path.dirname(__file__)))

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

if os.path.exists('config.py'):
    import config


HOST = os.getenv(HOST, config.host)
USER = os.getenv(USER, config.user)
PASSWD = os.getenv(PASSWD, config.passwd)
# HOST = os.getenv(HOST)
# USER = os.getenv('USER')
# PASSWD = os.getenv('PASSWD')

## CONNECTING TO MYSQL
mydb = mysql.connector.connect(
    host=HOST,
    user=USER,
    passwd=PASSWD
)

PLOTLY_LOGO = "/assets/favicon.ico"
REDDIT_LOGO = "https://external-preview.redd.it/iDdntscPf-nfWKqzHRGFmhVxZm4hZgaKe5oyFws-yzA.png?auto=webp&s=38648ef0dc2c3fce76d5e1d8639234d8da0152b2"
TWITTER_LOGO = "https://assets.stickpng.com/images/580b57fcd9996e24bc43c53e.png"
with open("tickers.pickle", "rb") as f:
    ticker_list = pickle.load(f)

colors = {
    "background": "#FFFFFF",
    "text": "#000000"
}

#-------------------------------HELPER FUNCTIONS--------------------------------

# GENERATE STOCK STATS TABLE
def getStockTable(df, stock_info):

    last_day = df.iloc[-1,1:6]

    # OPEN PRICE
    last_open_price = last_day['Open']
    last_open_price = f'{last_open_price:,.2f}'

    # FORMAT THE DAY RANGE OF PRICE
    low_day = last_day['Low']
    high_day = last_day['High']
    range_day = f'{low_day:,.2f}'+' - '+f'{high_day:,.2f}'

    # OBTAIN AND FORMAT 52 WEEKS RANGE OF PRICE
    low_52weeks = df['Low'].min()
    high_52weeks = df['High'].max()
    range_52weeks = f'{low_52weeks:,.2f}'+' - '+f'{high_52weeks:,.2f}'

    # FORMAT VOLUMNE AND AVERAGE VOLUME
    vol = last_day['Volume']
    vol = f'{vol:,.0f}'
    avg_vol = stock_info['averageVolume10days']
    avg_vol = f'{avg_vol:,.0f}'

    # OBTAIN SHARES OUTSTANDING
    shareOutstanding = stock_info['sharesOutstanding']

    # CALCULATE MARKET CAP AND FORMAT IT
    mktcap = last_day['Close']*shareOutstanding
    mktcap = f'{mktcap:,.0f}'

    # FORMAT BETA
    beta = stock_info['beta']
    beta = f'{beta:.2f}'

    # FORMAT PE AND FORWARD PE, IF NO PE, PE NOT IN THE DICTIONARY
    if 'trailingPE' in stock_info:
        pe = stock_info['trailingPE']
        pe = f'{pe:.2f}'
    else:
        pe = 'N/A'
    if 'forwardPE' in stock_info and stock_info['forwardPE'] != None:
        fpe = stock_info['forwardPE']
        fpe = f'{fpe:.2f}'
    else:
        fpe = 'N/A'

    # FORMAT EPS
    eps = stock_info['trailingEps']
    eps = f'{eps:.2f}'

    # FORMAT PROFIT MARGIN
    margin = stock_info['profitMargins']
    margin = f'{margin:.2f}'

    # PREPARE DATA FOR DIVIDENT RATE
    if stock_info['dividendRate'] is None or stock_info['dividendRate']=='':
        dividend = 'N/A'
    else:
        dividend = stock_info['dividendRate']

    # PREPATE DATA FOR EX-DIVIDEND DATE
    if stock_info['exDividendDate'] is not None:
        ex_dividend_date = datetime.fromtimestamp(stock_info['exDividendDate'])
        ex_dividend_date = ex_dividend_date.strftime('%m-%d-%Y')
    else: 
        ex_dividend_date = 'N/A'

    return html.Table([
        html.Tr([html.Td('Industry'), html.Td(),
                    html.Td(stock_info['industry'])]),
        html.Tr([html.Td('Previous Close'), html.Td(),
                    html.Td(stock_info['previousClose'])]),
        html.Tr([html.Td('Open'), html.Td(),
                    html.Td(last_open_price)]),
        html.Tr([html.Td('Day Range'), html.Td(),
                    html.Td(range_day)]),
        html.Tr([html.Td('52 Weeks Range'), html.Td(),
                    html.Td(range_52weeks)]),
        html.Tr([html.Td('Volume'), html.Td(),
                    html.Td(vol)]),
        html.Tr([html.Td('Average Volume'), html.Td(),
                    html.Td(avg_vol)]),
        html.Tr([html.Td('Market Capitalization'), html.Td(),
                    html.Td(mktcap)]),
        html.Tr([html.Td('Beta'), html.Td(),
                    html.Td(beta)]),
        html.Tr([html.Td('PE'), html.Td(),
                    html.Td(pe)]),
        html.Tr([html.Td('Forward PE'), html.Td(),
                    html.Td(fpe)]),
        html.Tr([html.Td('Earning Per Share (EPS)'), html.Td(),
                    html.Td(eps)]),
        html.Tr([html.Td('Profit Margin'), html.Td(),
                    html.Td(margin)]),
        html.Tr([html.Td('Dividend'), html.Td(),
                    html.Td(dividend)]),
        html.Tr([html.Td('Ex-Dividend Date'), html.Td(),
                    html.Td(ex_dividend_date)]),
        html.Tr([html.Td('Shares Outstanding'), html.Td(),
                    html.Td(f'{shareOutstanding:,.0f}')]),
        html.Tr([html.Td('Business Summary'), html.Td(),
            html.Td(stock_info['longBusinessSummary'])]),
        ])

"""
#---------------------------PAGE LAYOUT AND CONTENTS----------------------------

In an effort to clean up the code a bit, we decided to break it apart into
sections. For instance: LEFT_COLUMN is the input controls you see in that gray
box on the top left. The body variable is the overall structure which most other
sections go into. This just makes it ever so slightly easier to find the right
spot to add to or change without having to count too many brackets.
"""

NAVBAR = dbc.Navbar(
    children=[
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(
                        html.Img(
                            src=PLOTLY_LOGO, 
                            height="40px", 
                            style={"marginLeft": 35}
                        ),
                        style={"maxWidth": "40%"}
                    ),
                    dbc.Col(
                        dbc.NavbarBrand("Ticker Buzz", 
                            className="ml-2", 
                            style={"fontSize": 24}
                        )
                    ),
                ],
                align="center",
                no_gutters=True,
            ),
            href="https://github.com/matteeyao",
        )
    ],
    color="dark",
    dark=True,
    sticky="top",
    style={"height": 60}
)

LEFT_COLUMN = dbc.Jumbotron(
    [
        dcc.Loading(
            id="loading-stock-info",
            children=[
                dbc.Alert(
                    "Unable to obtain company information.",
                    id="no-stock-info-alert",
                    color="warning",
                    style={"display": "none"},
                ),
                html.H4(id='stock-name', className="display-5"),
                html.Hr(className="my-2"),
                html.Label(dbc.Row([
                    dbc.Col([
                        html.Div(
                            id='stock-price', 
                            style={"display": "inline-block", "width": "20%", "fontSize": "150%"}
                        )
                    ], md=4),
                    dbc.Col([
                        html.Div(id='stock-price-change')
                    ], md=4),
                    dbc.Col([
                        html.Div(id='stock-price-percent-change')
                    ], md=4),
                ], style={"marginBottom": 20}), className="lead"),
                html.Div([
                    html.Div(
                        [
                            dbc.Table(
                                id="stock-table-info",
                                className="stock-table-info",
                                style={"width": "100%"}
                            )
                        ],
                        className="stock-table-info-container",
                        style={"height": 590, "overflowY": "auto", "marginBottom": 10}
                    )
                ]),
                html.P(
                    "(Source: Yahoo Finance)",
                    style={"fontSize": 10, "font-weight": "lighter", "position": "absolute", "bottom": "4.5%"},
                ),
            ],
            type="circle",
        )  
    ],
    style={"height": 756, "padding": "1.5rem 3rem"}
)

TICKER_DASHBOARD = [
    dbc.CardHeader(html.H5("Live Dashboard")),
    dbc.CardBody(
        [
            dcc.Loading(
                id="loading-stock-chart",
                children=[
                    dbc.Alert(
                        "Not enough data to render this chart, please adjust the filters",
                        id="no-stock-chart-alert",
                        color="warning",
                        style={"display": "none"},
                    ),
                    dbc.Row(
                        [
                            dbc.Col(html.P("Select ticker:"), md=5),
                            dbc.Col(html.P("Choose chart type:"), md=5),
                            dbc.Col(
                                [
                                    dcc.Dropdown(
                                        id="stock_ticker",
                                        options=[{
                                                "label": s,
                                                "value": s,
                                            } for s in ticker_list.keys()],
                                        searchable=True,
                                        value=str("Walt Disney Company (DIS)"),
                                        placeholder="Select a ticker...",
                                    )
                                ],
                                width=5,
                                style={"paddingRight": 5}
                            ),
                            dbc.Col(
                                [
                                    dcc.Dropdown(
                                        id="chart",
                                        options=[
                                            {"label": "Line", "value": "Line"},
                                            {"label": "Candlestick", "value": "Candlestick"},
                                            {"label": "Simple Moving Average", "value": "SMA"},
                                            {"label": "Exponential Moving Average", "value": "EMA",},
                                            {"label": "MACD", "value": "MACD"},
                                            {"label": "RSI", "value": "RSI"},
                                            {"label": "OHLC", "value": "OHLC"},
                                        ],
                                        value="Line",
                                        style={"marginRight": "-10px"},
                                    )
                                ],
                                width=5,
                            ),
                            dbc.Col(
                                [dbc.Button(
                                    "Chart",
                                    id="submit-button-state",
                                    className="submit-chart-button",
                                    n_clicks=1,
                                )],
                                width=2,
                            )
                        ],
                        no_gutters=True,
                    ),
                    dbc.Row(
                        [
                            dcc.Graph(
                                id="live-stock-chart",
                                className="live-stock-chart",
                                config={
                                    "displaylogo": False,
                                    "modeBarButtonsToRemove": ["pan2d", "lasso2d"],
                                },
                            ),            
                        ]
                    ),
                ],
                type="default",
            ),
        ],
        style={"marginTop": 0, "marginBottom": 0},
    ),
]

REDDIT_COMMENTS_CONTAINER = [
    dbc.CardHeader(html.H5("Reddit Comment Mention Feed")),
    dbc.Alert(
        "Unable to connect to Reddit at this time.",
        id="no-data-alert-reddit",
        color="warning",
        style={"display": "none"},
    ),
    dbc.CardBody(
        [
            dcc.Loading(
                id="loading-reddit-comments", 
                children=[
                    dbc.Alert(
                        "Unable to connect to Reddit at this time.",
                        id="no-reddit-feed-alert",
                        color="warning",
                        style={"display": "none"},
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Div(
                                    id='reddit-comments',
                                    style={"display": "flex", "justifyContent": "horizontal", "overflowX": "auto","minHeight": 433}
                                ),
                                width=12
                            )
                        ]
                    ),
                ],
                type="default"
            ),
            html.Hr(),
        ],
        style={"minHeight": 446}
    ),
]

TWITTER_TWEETS_CONTAINER = [
    dbc.CardHeader(html.H5("Twitter Mention Feed")),
    dbc.Alert(
        "Unable to connect to Twitter at this time.",
        id="no-data-alert-twitter",
        color="warning",
        style={"display": "none"},
    ),
    dbc.CardBody(
        [
            dcc.Loading(
                id="loading-twitter-tweets", 
                children=[
                    dbc.Alert(
                        "Unable to connect to Twitter at this time.",
                        id="no-twitter-feed-alert",
                        color="warning",
                        style={"display": "none"},
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Div(
                                    id='twitter-tweets',
                                    style={"display": "flex", "justifyContent": "horizontal", "overflowX": "auto", "minHeight": 433}
                                ),
                                width=12
                            )
                        ]
                    ),
                ],
                type="default"
            ),
            html.Hr(),
        ],
        style={"minHeight": 446}
    ),
]


BODY = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(LEFT_COLUMN, md=4, align="center"),
                dbc.Col(dbc.Card(TICKER_DASHBOARD), md=8),
            ],
            style={"marginTop": 30},
        ),
        dbc.Row([dbc.Col(dbc.Card(REDDIT_COMMENTS_CONTAINER)),], style={"marginTop": 15}),
        dbc.Row([dbc.Col(dbc.Card(TWITTER_TWEETS_CONTAINER)),], style={"marginTop": 30, "marginBottom": 15}),
    ],
    className="mt-12",
)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.title = "Ticker Buzz"

app.layout = html.Div(children=[NAVBAR, BODY])

#-----------------------------CALLBACK FETCH STOCK------------------------------

@app.callback(
    # OUTPUT
    [Output('stock-name','children'), # STOCK NAME
    Output('stock-price','children'), # CURRENT STOCK PRICE
    Output('stock-price-change','children'), # PRICE CHANGE
    Output('stock-price-change','style'), # PRICE CHANGE FONT COLOR
    Output('stock-price-percent-change','children'), # PRICE PERCENT CHANGE
    Output('stock-price-percent-change','style'), # PRICE PERCENT CHANGE FONT COLOR
    Output('stock-table-info','children'), # STOCK TABLE STATS
    Output("live-stock-chart", "figure")],
    # INPUT
    [Input('submit-button-state','n_clicks')], # BUTTON
    # STATE
    [State("stock_ticker", "value"), # TICKER INPUT
     State("chart", "value")],
)

def get_ticker(n_clicks, ticker, chart_name):

    ticker = ticker_list[ticker][0]

    if n_clicks >= 1:  # CHECKING FOR USER TO CLICK SUBMIT BUTTON

        # LOADING DATA
        start_date = datetime.now().date() - timedelta(days=5 * 365)
        end_data = datetime.now().date()
        df = yf.get_data(
            ticker, start_date=start_date, end_date=end_data, interval="1d"
        )
        stock = Sdf(df)

        # -*- SELECTING GRAPH TYPE -*-

        # LINE PLOT
        if chart_name == "Line":
            fig = go.Figure(
                data=[
                    go.Scatter(
                        x=list(df.index), y=list(df.close), fill="tozeroy", name="Adj. Close"
                    )
                ],
                layout={
                    "showlegend": True,
                    "plot_bgcolor": colors["background"],
                    "paper_bgcolor": colors["background"],
                    "font": {"color": colors["text"]},
                    'margin': dict(l=40, r=20, t=60, b=20),
                },
            )

            fig.update_xaxes(
                rangeslider_visible=True,
                rangeselector=dict(
                    activecolor="rgb(177,183,248)",
                    bgcolor=colors["background"],
                    buttons=list(
                        [
                            dict(count=7, label="10D",
                                 step="day", stepmode="backward"),
                            dict(
                                count=15, label="15D", step="day", stepmode="backward"
                            ),
                            dict(
                                count=1, label="1m", step="month", stepmode="backward"
                            ),
                            dict(
                                count=3, label="3m", step="month", stepmode="backward"
                            ),
                            dict(
                                count=6, label="6m", step="month", stepmode="backward"
                            ),
                            dict(
                                count=1, label="1y", step="year", stepmode="backward"
                            ),
                            dict(
                                count=5, label="5y", step="year", stepmode="backward"
                            ),
                            dict(
                                count=1, label="YTD", step="year", stepmode="todate"
                            ),
                            dict(step="all"),
                        ]
                    ),
                )
            )

        # CANDLESTICK
        if chart_name == "Candlestick":
            fig = go.Figure(
                data=[
                    go.Candlestick(
                        x=list(df.index),
                        open=list(df.open),
                        high=list(df.high),
                        low=list(df.low),
                        close=list(df.close),
                        name="Candlestick",
                    )
                ],
                layout={
                    "showlegend": True,
                    "plot_bgcolor": colors["background"],
                    "paper_bgcolor": colors["background"],
                    "font": {"color": colors["text"]},
                    'margin': dict(l=40, r=20, t=60, b=20),
                },
            )

            fig.update_xaxes(
                rangeslider_visible=True,
                rangeselector=dict(
                    activecolor="rgb(177,183,248)",
                    bgcolor=colors["background"],
                    buttons=list(
                        [
                            dict(count=7, label="10D",
                                 step="day", stepmode="backward"),
                            dict(
                                count=15, label="15D", step="day", stepmode="backward"
                            ),
                            dict(
                                count=1, label="1m", step="month", stepmode="backward"
                            ),
                            dict(
                                count=3, label="3m", step="month", stepmode="backward"
                            ),
                            dict(
                                count=6, label="6m", step="month", stepmode="backward"
                            ),
                            dict(
                                count=1, label="1y", step="year", stepmode="backward"
                            ),
                            dict(
                                count=5, label="5y", step="year", stepmode="backward"
                            ),
                            dict(
                                count=1, label="YTD", step="year", stepmode="todate"
                            ),
                            dict(step="all"),
                        ]
                    ),
                ),
            )

        # SIMPLE MOVING AVERAGE
        if chart_name == "SMA":
            close_ma_10 = df.close.rolling(10).mean()
            close_ma_15 = df.close.rolling(15).mean()
            close_ma_30 = df.close.rolling(30).mean()
            close_ma_100 = df.close.rolling(100).mean()
            fig = go.Figure(
                data=[
                    go.Scatter(
                        x=list(close_ma_10.index), y=list(close_ma_10), name="10 Days"
                    ),
                    go.Scatter(
                        x=list(close_ma_15.index), y=list(close_ma_15), name="15 Days"
                    ),
                    go.Scatter(
                        x=list(close_ma_30.index), y=list(close_ma_15), name="30 Days"
                    ),
                    go.Scatter(
                        x=list(close_ma_100.index), y=list(close_ma_15), name="100 Days"
                    ),
                ],
                layout={
                    "showlegend": True,
                    "plot_bgcolor": colors["background"],
                    "paper_bgcolor": colors["background"],
                    "font": {"color": colors["text"]},
                    'margin': dict(l=40, r=20, t=60, b=20),
                },
            )

            fig.update_xaxes(
                rangeslider_visible=True,
                rangeselector=dict(
                    activecolor="rgb(177,183,248)",
                    bgcolor=colors["background"],
                    buttons=list(
                        [
                            dict(count=7, label="10D",
                                 step="day", stepmode="backward"),
                            dict(
                                count=15, label="15D", step="day", stepmode="backward"
                            ),
                            dict(
                                count=1, label="1m", step="month", stepmode="backward"
                            ),
                            dict(
                                count=3, label="3m", step="month", stepmode="backward"
                            ),
                            dict(
                                count=6, label="6m", step="month", stepmode="backward"
                            ),
                            dict(count=1, label="1y", step="year",
                                 stepmode="backward"),
                            dict(count=5, label="5y", step="year",
                                 stepmode="backward"),
                            dict(count=1, label="YTD",
                                 step="year", stepmode="todate"),
                            dict(step="all"),
                        ]
                    ),
                ),
            )

        # OPEN_HIGH_LOW_CLOSE
        if chart_name == "OHLC":
            fig = go.Figure(
                data=[
                    go.Ohlc(
                        x=df.index,
                        open=df.open,
                        high=df.high,
                        low=df.low,
                        close=df.close,
                    )
                ],
                layout={
                    "showlegend": True,
                    "plot_bgcolor": colors["background"],
                    "paper_bgcolor": colors["background"],
                    "font": {"color": colors["text"]},
                    'margin': dict(l=40, r=20, t=60, b=20),
                },
            )

            fig.update_xaxes(
                rangeslider_visible=True,
                rangeselector=dict(
                    activecolor="rgb(177,183,248)",
                    bgcolor=colors["background"],
                    buttons=list(
                        [
                            dict(count=7, label="10D",
                                 step="day", stepmode="backward"),
                            dict(
                                count=15, label="15D", step="day", stepmode="backward"
                            ),
                            dict(
                                count=1, label="1m", step="month", stepmode="backward"
                            ),
                            dict(
                                count=3, label="3m", step="month", stepmode="backward"
                            ),
                            dict(
                                count=6, label="6m", step="month", stepmode="backward"
                            ),
                            dict(count=1, label="1y", step="year",
                                 stepmode="backward"),
                            dict(count=5, label="5y", step="year",
                                 stepmode="backward"),
                            dict(count=1, label="YTD",
                                 step="year", stepmode="todate"),
                            dict(step="all"),
                        ]
                    ),
                ),
            )

        # EXPONENTIAL MOVING AVERAGE
        if chart_name == "EMA":
            close_ema_10 = df.close.ewm(span=10).mean()
            close_ema_15 = df.close.ewm(span=15).mean()
            close_ema_30 = df.close.ewm(span=30).mean()
            close_ema_100 = df.close.ewm(span=100).mean()
            fig = go.Figure(
                data=[
                    go.Scatter(
                        x=list(close_ema_10.index), y=list(close_ema_10), name="10 Days"
                    ),
                    go.Scatter(
                        x=list(close_ema_15.index), y=list(close_ema_15), name="15 Days"
                    ),
                    go.Scatter(
                        x=list(close_ema_30.index), y=list(close_ema_30), name="30 Days"
                    ),
                    go.Scatter(
                        x=list(close_ema_100.index),
                        y=list(close_ema_100),
                        name="100 Days",
                    ),
                ],
                layout={
                    "showlegend": True,
                    "plot_bgcolor": colors["background"],
                    "paper_bgcolor": colors["background"],
                    "font": {"color": colors["text"]},
                    "margin": dict(l=60, r=20, t=60, b=0),
                },
            )

            fig.update_xaxes(
                rangeslider_visible=True,
                rangeselector=dict(
                    activecolor="rgb(177,183,248)",
                    bgcolor=colors["background"],
                    buttons=list(
                        [
                            dict(count=7, label="10D",
                                 step="day", stepmode="backward"),
                            dict(
                                count=15, label="15D", step="day", stepmode="backward"
                            ),
                            dict(
                                count=1, label="1m", step="month", stepmode="backward"
                            ),
                            dict(
                                count=3, label="3m", step="month", stepmode="backward"
                            ),
                            dict(
                                count=6, label="6m", step="month", stepmode="backward"
                            ),
                            dict(count=1, label="1y", step="year",
                                 stepmode="backward"),
                            dict(count=5, label="5y", step="year",
                                 stepmode="backward"),
                            dict(count=1, label="YTD",
                                 step="year", stepmode="todate"),
                            dict(step="all"),
                        ]
                    ),
                ),
            )

        # MOVING AVERAGE CONVERGENCE DIVERGENCE
        if chart_name == "MACD":
            df["MACD"], df["signal"], df["hist"] = (
                stock["macd"],
                stock["macds"],
                stock["macdh"],
            )
            fig = go.Figure(
                data=[
                    go.Scatter(x=list(df.index), y=list(df.MACD), name="MACD"),
                    go.Scatter(x=list(df.index), y=list(
                        df.signal), name="Signal"),
                    go.Scatter(
                        x=list(df.index),
                        y=list(df["hist"]),
                        line=dict(color="royalblue", width=2, dash="dot"),
                        name="Histogram",
                    ),
                ],
                layout={
                    "showlegend": True,
                    "plot_bgcolor": colors["background"],
                    "paper_bgcolor": colors["background"],
                    "font": {"color": colors["text"]},
                    "margin": dict(l=60, r=20, t=60, b=0),
                },
            )

            fig.update_xaxes(
                rangeslider_visible=True,
                rangeselector=dict(
                    activecolor="rgb(177,183,248)",
                    bgcolor=colors["background"],
                    buttons=list(
                        [
                            dict(count=7, label="10D",
                                 step="day", stepmode="backward"),
                            dict(
                                count=15, label="15D", step="day", stepmode="backward"
                            ),
                            dict(
                                count=1, label="1m", step="month", stepmode="backward"
                            ),
                            dict(
                                count=3, label="3m", step="month", stepmode="backward"
                            ),
                            dict(
                                count=6, label="6m", step="month", stepmode="backward"
                            ),
                            dict(count=1, label="1y", step="year",
                                 stepmode="backward"),
                            dict(count=5, label="5y", step="year",
                                 stepmode="backward"),
                            dict(count=1, label="YTD",
                                 step="year", stepmode="todate"),
                            dict(step="all"),
                        ]
                    ),
                ),
            )

        # RELATIVE STRENGTH INDEX
        if chart_name == "RSI":
            rsi_6 = stock["rsi_6"]
            rsi_12 = stock["rsi_12"]
            fig = go.Figure(
                data=[
                    go.Scatter(x=list(df.index), y=list(
                        rsi_6), name="RSI 6 Day"),
                    go.Scatter(x=list(df.index), y=list(
                        rsi_12), name="RSI 12 Day"),
                ],
                layout={
                    "showlegend": True,
                    "plot_bgcolor": colors["background"],
                    "paper_bgcolor": colors["background"],
                    "font": {"color": colors["text"]},
                    "margin": dict(l=60, r=20, t=60, b=0),
                },
            )
            fig.update_xaxes(
                rangeslider_visible=True,
                rangeselector=dict(
                    activecolor="rgb(177,183,248)",
                    bgcolor=colors["background"],
                    buttons=list(
                        [
                            dict(count=7, label="10D",
                                 step="day", stepmode="backward"),
                            dict(
                                count=15, label="15D", step="day", stepmode="backward"
                            ),
                            dict(
                                count=1, label="1m", step="month", stepmode="backward"
                            ),
                            dict(
                                count=3, label="3m", step="month", stepmode="backward"
                            ),
                            dict(
                                count=6, label="6m", step="month", stepmode="backward"
                            ),
                            dict(count=1, label="1y", step="year",
                                 stepmode="backward"),
                            dict(count=5, label="5y", step="year",
                                 stepmode="backward"),
                            dict(count=1, label="YTD",
                                 step="year", stepmode="todate"),
                            dict(step="all"),
                        ]
                    ),
                ),
            )

        # FOR DEFAULT SETTING
        if ticker == '':
            return 'Please select a stock ticker', \
                    '','',{'width':'20%', 'display':'inline-block', 'font-size': '150%'},'', \
                    {'width':'20%', 'display':'inline-block', 'font-size': '150%'}, None, {'data':None}
                
        # OBTAIN STOCK PRICE AND STATS
        stock = yfinance.Ticker(ticker)

        # CATCH IF STOCK EXISTS
        if stock.history(period='ytd').shape[0] == 0:
            return 'Something went wrong', '$##.##', '##.##', \
                    {'width':'20%', 'display':'inline-block', 'font-size': '150%'}, '##.##%', \
                    {'width':'20%', 'display':'inline-block', 'font-size': '150%'}, None, {'data':None}

        ### STOCK STATS FOR INFO BOX ###
        try:
            # NAME AND PRICE
            stock_name = stock.info['longName']
            price_list = stock.history(period='1y')['Close'].tolist()
            price = f'${price_list[-1]:.2f}'
            # PRICE CHANGE
            price_change = price_list[-1] - price_list[-2]
            price_percent_change = (price_list[-1]/price_list[-2])-1

            if price_change > 0:
                price_change_color = {'color':'green'}
            else:
                price_change_color = {'color':'red'}

            price_change_color['display']= 'inline-block'
            price_change_color['width']= '20%'
            price_change_color['font-size'] = '150%'

            price_change = f'{price_change:.2f}'
            price_percent_change = f'{price_percent_change*100:,.2f}%'

            table = getStockTable(stock.history(period='1y').reset_index(), stock.info)

        except:
            return 'Something went wrong(2)', '$##.##', '##.##', \
                {'width':'20%', 'display':'inline-block', 'font-size': '150%'}, '##.##%', \
                {'width':'20%', 'display':'inline-block', 'font-size': '150%'}, None, {'data':None}

    return stock_name, price, price_change, price_change_color, \
            price_percent_change, price_change_color, table, fig

#------------------------FETCH REDDIT/TWITTER MENTIONS--------------------------

def generate_reddit_cards(df):
    return [dbc.Card(
        [
            dbc.CardHeader(
                children=[
                    html.Img(
                        src=REDDIT_LOGO, 
                        height="40px", 
                        style={"marginRight": 10}
                    ),
                    html.Div(
                        "r/"+d[0],
                        style={"fontSize": 16,}
                    )
                ],
                style={"display":"flex", "alignItems": "center"}
            ),
            dbc.CardBody(
                [
                    html.P(
                        (d[2][0:419:1], d[2][0:420:1])[d[2][420] == " "]+"..." if len(d[2]) > 420 else d[2],
                        className="card-text",
                    ),
                ]            
            )
        ],
        className="ticker-mention",
        color="dark",
        inverse=True
    ) for d in df.values.tolist()]

def generate_twitter_cards(df):
    return [dbc.Card(
        [
            dbc.CardHeader(
                children=[
                    html.Img(
                        src=TWITTER_LOGO, 
                        height="40px", 
                        style={"marginRight": 10}
                    ),
                ],
                style={"display":"flex", "alignItems": "center"}
            ),
            dbc.CardBody(
                [
                    html.P(
                        (d[1][0:419:1], d[1][0:420:1])[d[2][420] == " "]+"..." if len(d[1]) > 420 else d[1],
                        className="card-text",
                    ),
                ]            
            )
        ],
        className="ticker-mention",
        color="dark",
        inverse=True
    ) for d in df.values.tolist()]

@app.callback(
    # OUTPUT
    [Output('reddit-comments','children'),
    Output('twitter-tweets','children')],
    # INPUT
    [Input('submit-button-state','n_clicks')], # BUTTON
    # STATE
    [State("stock_ticker", "value")] # TICKER INPUT
)

def update_mentions(n_clicks, ticker):

    company = ticker_list[ticker][1]
    ticker = ticker_list[ticker][0]

    if n_clicks >= 1: # CHECKING FOR USER TO CLICK SUBMIT BUTTON

        try:
            reddit_df = pd.read_sql(
                """SELECT * FROM reddit_data.reddit_data_sentiment 
                WHERE body LIKE %s AND date_time > ADDDATE(date_time, -1)
                OR body LIKE %s AND date_time > ADDDATE(date_time, -1)
                ORDER BY date_time DESC LIMIT 20;""", con=mydb, params=('%'+company+'%', '%$'+ticker+' %',))
            twitter_df = pd.read_sql(
                """SELECT * FROM twitter_data.twitter_data_sentiment 
                WHERE tweet LIKE %s AND date_time > ADDDATE(date_time, -1)
                OR tweet LIKE %s AND date_time > ADDDATE(date_time, -1)
                ORDER BY date_time DESC LIMIT 20;""", con=mydb, params=('%'+company+'%', '%$'+ticker+' %',))

            reddit_df = reddit_df[['subreddit','date_time','body']]
            twitter_df = twitter_df[['date_time', 'tweet']]

            return generate_reddit_cards(reddit_df), generate_twitter_cards(twitter_df)

        except Exception as e:
            with open('errors.txt', 'a') as f:
                f.write(str(e))
                f.write('\n')

#-------------------------------------------------------------------------------

server = app.server
dev_server = app.run_server
