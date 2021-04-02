from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import sys, os
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import datetime
import time
import pytz
from unidecode import unidecode
import pandas as pd
import json
from dotenv import load_dotenv

load_dotenv()

# INSERT YOUR TWITTER API KEY HERE 
ckey=os.getenv('CKEY')
csecret=os.getenv('CSECRET')
atoken=os.getenv('ATOKEN')
asecret=os.getenv('ASECRET')

# CONNECT TO A PSQL SERVER
# mydb = psycopg2.connect(
#     host=os.getenv('HOST'),
#     database=os.getenv('DATABASE'),
#     user=os.getenv('USER'),
#     password=os.getenv('PASSWD')
# )

## PUT YOUR URL IN AN ENVIRONMENT VARIABLE AND CONNECT.
engine=create_engine(os.getenv("DATABASE_URL"), echo=True)
# mydb=scoped_session(sessionmaker(bind=engine))

engine.execute("""CREATE TABLE IF NOT EXISTS twitter_data (
                    date_time TIMESTAMP,
                    tweet VARCHAR(2000)
                )""")

sqlFormula = "INSERT INTO twitter_data (date_time, tweet) VALUES (%s, %s)"

class listener(StreamListener):

    def on_data(self, data):
        all_data = json.loads(data) # use json.loads to load the string data from the Twitter API data
        current_time = datetime.datetime.now()
        tweet = str(all_data["text"])
        db = (current_time, tweet)
        engine.execute(sqlFormula, db)
        # mydb.commit()
        print("success")

    def on_error(self,status):
        print(status)

## Connecting to twitter and establishing a live stream
while (datetime.time(8, 00, 0, 0, pytz.timezone('America/Chicago')) < datetime.datetime.now().time() and datetime.datetime.now().time() < datetime.time(22, 00, 0, 0, pytz.timezone('America/Chicago'))):
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
