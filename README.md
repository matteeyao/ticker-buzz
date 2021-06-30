# [Ticker Buzz](https://tickerbuzzz.herokuapp.com/)

<img src="assets/ticker-buzz.gif" width="1000">

### Table of contents
1. [Background](#background)
2. [Functionality & MVP](#functionality)
3. [Architecture and technologies](#technologies)

## <a name="background"></a> Background

Ticker Buzz, a personal stock dashboard that combines the intelligence of Yahoo finance and several financial analysis chart types with live mentions regarding the stock that happen on Reddit.

Users of the stock dashboard are able to:

- [x] View charts and information of any North American publicly traded company (>1B EV)
- [x] Hover over each of the charts to discern a company's stock price throughout any point in time
- [x] Toggle between different stock chart analysis tools: Line, CandleStick, Exponential Moving Average, etc
- [x] View mentions of the company happing on reddit

## <a name="technologies"></a> Architecture and technologies

The project uses the following technologies:

* `Python` for abundance of data analysis dependencies
* `Dash` for data visualization
* `Pandas` for data manipulation and analysis of all the application's data
* `Yahoo Finance API` to provide all the technical and price information related to the company
* `Reddit API (PRAW)` to stream reddit comments into the application's postgres database
* `AWS Lambda` to continuously build the application's postgres database on the backend
* `SQLAlchemy` for ease in incorporating Heroku's postgres database into the python application

## What is Dash?
Dash is a productive Python framework for building web applications.
Written on top of Flask, Plotly.js, and React.js, Dash is ideal for building data visualization apps with highly custom user interfaces in pure Python. It's particularly suited for anyone who works with data in Python.
Through a couple of simple patterns, Dash abstracts away all of the technologies and protocols that are required to build an interactive web-based application. Dash is simple enough that you can bind a user interface around your Python code in an afternoon.
Dash apps are rendered in the web browser. You can deploy your apps to servers and then share them through URLs. Since Dash apps are viewed in the web browser, Dash is inherently cross-platform and mobile ready.
<br/>

## Quick start
1. Clone repo
2. install requirements.txt using pip install -r requirements.txt
3. Fill in your Twitter App credentials to reddit_stream.py. Go to apps.reddit.com to set that up if you need to.
4. Run reddit_stream.py to build database
5. If you're using this locally, you can run the application with the dev_server.py script. If you want to deploy this to a webserver, see my deploying Dash application tutorial
