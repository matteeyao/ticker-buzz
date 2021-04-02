from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import psycopg2
import sys, os
import praw
import datetime
import pytz
from unidecode import unidecode
import time
from dotenv import load_dotenv

load_dotenv()


# Initialize reddit api here 
reddit = praw.Reddit(
    client_id=os.getenv('CLIENT_ID'),
    client_secret=os.getenv('CLIENT_SECRET'),
    username=os.getenv('USERNAME'),
    password=os.getenv('PASSWORD'),
    user_agent=os.getenv('USER_AGENT')
)

# CONNECT TO A PSQL SERVER
# mydb = psycopg2.connect(
#     host=os.getenv('HOST'),
#     database=os.getenv('DATABASE'),
#     user=os.getenv('USER'),
#     password=os.getenv('PASSWD'),
# )

## PUT YOUR URL IN AN ENVIRONMENT VARIABLE AND CONNECT.
engine=create_engine(os.getenv("DATABASE_URL"), echo=True)

# Title and body would be used for the sentiment analysis and for counting the number of times a particular ticker is mentioned 
engine.execute("""CREATE TABLE IF NOT EXISTS reddit_data (
                    date_time TIMESTAMP,
                    subreddit VARCHAR(500),
                    title VARCHAR(500),
                    body VARCHAR(2000)
                )""")

# pushing the data to the database 
sqlFormula = "INSERT INTO reddit_data (date_time, subreddit, title, body) VALUES (%s, %s, %s, %s)"

## Streaming comments from reddit 
while (datetime.time(8, 00, 0, 0, pytz.timezone('America/Chicago')) < datetime.datetime.now().time() and datetime.datetime.now().time() < datetime.time(22, 00, 0, 0, pytz.timezone('America/Chicago'))):
    try:
        # list of subreddits to be tracked -- you can add the ones you think are important to track 
        subreddit = reddit.subreddit("wallstreetbets+investing+stocks+pennystocks+weedstocks+StockMarket+Trading+Daytrading+algotrading")
        for comment in subreddit.stream.comments(skip_existing=True):
                current_time = datetime.datetime.now()
                subreddit = str(comment.subreddit)
                title = str(comment.link_title)
                body = str(comment.body)
                if len(body) < 2000:
                    body = body
                elif len(body) > 2000:
                    body = "data is too large" ## very rare situation - less than 0.1% of the cases have comment more than 2000 characters 
                db=(current_time,subreddit,title,body)
                engine.execute(sqlFormula, db)

    # Keep an exception so that in case of error you dont hit the api multiple times and also your code wont crash on the vm
    except Exception as e:
        print(str(e))
        time.sleep(10)