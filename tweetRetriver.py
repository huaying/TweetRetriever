#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tweepy
import urllib
from firebase import firebase
import us_states
import random
import time
import re


# to-do
# integrate the format of hashtag name
# restrict the lang to only eng
# find trendlist

class TweetRetriver:
    
    consumer_key = "RkVxqW7o8ZQmXzmADaWvZabc7"
    consumer_secret = "qjnOyNEXb0ue2HftH6XdwGyMK20KqsJzNur5iIGPyFYIiKjRVS"
    access_token = "1168232528-5Ue02g8NqfMi3yHYoZemam0EAyvR0sIX9wI9zsA"
    access_token_secret = "gd357WJrt5ro4250kCrtulRGumns2Q6nkXAwSRiLaGABl"
    api = None
    wistunnel_db = None

    def __init__(self):
        self.wistunnel_db = WisTunnelDatabase()
        self.authenticate()
        self.process()
        #print len(self.searchHashTag("Trump"))
        #self.getTrendList()
    
    def process(self):
        trends = self.getTrendList()
        print "Trends: ",[trend['name'] for trend in trends]

        for trend in trends:
            tweets = self.searchHashTag('',trend)
            hashtag = re.sub(r'^#','',trend['name'])
            self.wistunnel_db.addHashTag(hashtag)
            for tweet in tweets:
                self.importComment(tweet,hashtag)

    def authenticate(self):
        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)
        self.api = tweepy.API(auth)

    def searchHashTag(self,hashtag,trend=None):
        print "searchHashTag: ",hashtag
        rlt = []
        query = ''
        if not trend: query=urllib.quote_plus("#"+hashtag)
        else: query = trend['query']
        for tweet in self.limit_handled(tweepy.Cursor(self.api.search,q=query).items(1000)):
            if not re.search(r'https\:\/\/t',tweet.text) and not re.search(u'…',tweet.text):
                rlt.append(tweet)
                #print re.sub(r'^RT .*?\:\s',"",tweet.text)
        return rlt
    
    def importComment(self,tweet,hashtag):
        db = self.wistunnel_db

        generatedUser = db.getRandomUser()
        db.addUser(generatedUser)

        db.addComment(tweet.id_str,re.sub(r'^RT .*?\:\s',"",tweet.text),hashtag,generatedUser.keys()[0])
        print tweet.text.encode('utf-8'), hashtag.encode('utf-8')

    def getTrendList(self):
        jsonRlt = self.api.trends_place(1)
        return jsonRlt[0]['trends']

    #helper
    def limit_handled(self,cursor):
        while True:
            try:
                yield cursor.next()
            except tweepy.TweepError:
                print "wait for 15 mins and refetch"
                time.sleep(15*60)

class WisTunnelDatabase:

    firebase_url = 'https://torrid-inferno-2138.firebaseio.com/'
    db = None

    def __init__(self):
        self.connect()
        #print self.db.get('hashtags',None)
        #print self.addHashTag('3')
        #self.addUser(self.getRandomUser())
        #print [self.getRandomUser() for i in range(10)]
    
    def connect(self):
        self.db = firebase.FirebaseApplication(self.firebase_url,None)

    def addHashTag(self,name):
        self.db.patch('/hashtags',{name:{'like':'0','neutral':'0','unlike':'0'}})

    def addComment(self,comment_id,content,hashtag,userid):
        self.db.patch('/comments',{comment_id:{'belong_to_hashtag':hashtag,'content':content,'num_of_like':'0','num_of_unlike':'0','userid':userid}})

    def addUser(self,user):
        self.db.patch('/users',user)

    def getRandomUser(self):
        return {
                int(time.time()*1000000):{
                    "nickname":"twitter_user",
                    #"location":random.choice(us_states.states_arr),
                    "location":self.random_distr(us_states.states),
                    "gender": random.choice(['male','female']),
                    "age": int(random.gauss(26,7))
                    }
                }

    #helper 
    #get random using probability
    def random_distr(self,l):
        r = random.uniform(0, 1)
        s = 0
        for item, prob in l:
            s += prob/100
            if s >= r:
                return item
        return item  # Might occur because of floating point inaccuraciesV

TweetRetriver()




















