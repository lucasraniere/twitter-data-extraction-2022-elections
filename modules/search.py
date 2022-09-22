import tweepy as tw
from modules.tweets_collection import Tweets_Collection
import modules.utils as utils
import math

class Search:
    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret, bearer_token, label):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.bearer_token = bearer_token
        self.sandbox_label = label
        self.auth = tw.OAuthHandler(self.consumer_key, self.consumer_secret)
        self.auth.set_access_token(self.access_token, self.access_token_secret)
        self.api = tw.API(self.auth, wait_on_rate_limit=True)


    def get_authenticator(self):
        return self.auth


    def get_api(self):
        return self.api


    def _recent(self, query: str, lang='pt', result_type='mixed', until=None, amount=math.inf):
        tweets_list = [tweet._json for tweet in tw.Cursor(
            self.api.search_tweets,
            q=query,
            lang=lang,
            result_type=result_type,
            until=until,
            tweet_mode='extended',
            count=100).items(amount)]
        return Tweets_Collection(tweets_list)


    def _30_days(self, query: str, lang=None, since=None, until=None, amount=math.inf):
        if lang is not None:
            query = query + f' lang:{lang}'
        if since is not None:
            since = utils.convert_date(since)
        if until is not None:
            until = utils.convert_date(until)
        tweets_list = [tweet._json for tweet in tw.Cursor(
            self.api.search_30_day,
            label=self.sandbox_label,
            query=query,
            fromDate=since,
            toDate=until,
            maxResults=100).items(amount)]
        return Tweets_Collection(tweets_list)


    def _archive(self, query: str, lang=None, since=None, until=None, amount=math.inf):
        if lang is not None:
            query = query + f' lang:{lang}'
        if since is not None:
            since = utils.convert_date(since)
        if until is not None:
            until = utils.convert_date(until)
        tweets_list = [tweets._json for tweets in tw.Cursor(
            self.api.search_full_archive,
            label=self.sandbox_label,
            query=query,
            fromDate=since,
            toDate=until,
            maxResults=100).items(amount)]
        return Tweets_Collection(tweets_list)
