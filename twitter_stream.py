# SET CHDIR TO CURRENT DIR
import os
import sys
sys.path.insert(0, os.path.realpath(os.path.dirname(__file__)))
os.chdir(os.path.realpath(os.path.dirname(__file__)))

from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import mysql.connector
import datetime
import time
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from unidecode import unidecode
import pandas as pd
import json
import config

analyzer = SentimentIntensityAnalyzer()

CKEY = os.getenv('SECRET_KEY', config.ckey)
CSECRET = os.getenv('SECRET_KEY', config.csecret)
ATOKEN = os.getenv('SECRET_KEY', config.atoken)
ASECRET = os.getenv('SECRET_KEY', config.asecret)
HOST = os.getenv('SECRET_KEY', config.host)
USER = os.getenv('SECRET_KEY', config.user)
PASSWD = os.getenv('SECRET_KEY', config.passwd)

# Insert your twitter API key here 
ckey = CKEY
csecret = CSECRET
atoken = ATOKEN
asecret = ASECRET

# CONNECT TO A MYSQL SERVER 
mydb = mysql.connector.connect(
    host=HOST,
    user=USER,
    passwd=PASSWD
)

# setup cursor
mycursor = mydb.cursor()

# Create a database for storing twitter data 
mycursor.execute("CREATE DATABASE IF NOT EXISTS twitter_data")

mycursor.execute("""CREATE TABLE IF NOT EXISTS twitter_data.twitter_data_sentiment
                (date_time DATETIME,
                tweet VARCHAR(2000),
                sentiment DECIMAL(5,4)
                )
                """)

sqlFormula = "INSERT INTO twitter_data.twitter_data_sentiment (date_time, tweet, sentiment) VALUES (%s, %s, %s)"

class listener(StreamListener):

    def on_data(self, data):
        all_data = json.loads(data) # use json.loads to load the string data from the Twitter API data
        current_time = datetime.datetime.now()
        tweet = str(all_data["text"])
        vs = analyzer.polarity_scores(unidecode(tweet))
        sentiment = vs['compound']
        db = (current_time, tweet, sentiment)
        mycursor.execute(sqlFormula, db)
        mydb.commit()

    def on_error(self,status):
        print(status)

## Connecting to twitter and establishing a live stream 
while True:
    try:
        auth = OAuthHandler(ckey, csecret)
        auth.set_access_token(atoken, asecret)
        twitterStream = Stream(auth, listener())
        twitterStream.filter(track=[
            "$A", "$B", "$C", "$D", "$E", "$F", "$G", "$H", "$I", "$J", "$K", "$L", "$M", "$N", "$O", "$P", "$Q", "$R", "$S", "$T", "$U", "$V", "$Q", "$X", "$Y", "$Z"
        ]) #this tracks any tweet with a $ symbol.
    except Exception as e:
        print(str(e))
        time.sleep(10)
