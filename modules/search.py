from netrc import netrc

from requests import request
import tweepy as tw
from modules.tweets_collection import Tweets_Collection
import modules.utils as utils
import math, time

fields = {
    'expansions' : ['author_id', 'referenced_tweets.id', 'in_reply_to_user_id',
                    'attachments.media_keys', 'geo.place_id', 'entities.mentions.username',
                    'referenced_tweets.id.author_id'],
    'media': ['type', 'url', 'public_metrics'],
    'place': ['full_name', 'country', 'country_code', 'place_type'],
    'tweet':['id', 'text', 'created_at', 'author_id', 'conversation_id', 'entities', 'geo', 'in_reply_to_user_id',
              'public_metrics', 'referenced_tweets', 'source'],
    'user': ['id', 'name', 'username', 'created_at', 'description', 'public_metrics']
}

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
        self.client = tw.Client(bearer_token=bearer_token, wait_on_rate_limit=False)


    def get_authenticator(self):
        return self.auth


    def get_api(self):
        return self.api

    def get_client(self):
        return self.client


    def _recent(self, query: str, lang='pt', result_type='mixed', until=None, amount=math.inf):
        tweets_list = [tweet._json for tweet in tw.Cursor(
            self.api.search_tweets,
            q=query,
            lang=lang,
            result_type=result_type,
            until=until,
            tweet_mode='extended',
            count=100).items(amount)]
        return Tweets_Collection(tweets_list, 'recent')


    def _30_days(self, query: str, lang=None, since=None, until=None, amount=math.inf):
        if lang:
            query = query + f' lang:{lang}'
        if since:
            since = utils.convert_date(since)
        if until:
            until = utils.convert_date(until)
        tweets_list = [tweet._json for tweet in tw.Cursor(
            self.api.search_30_day,
            label=self.sandbox_label,
            query=query,
            fromDate=since,
            toDate=until,
            maxResults=100).items(amount)]
        return Tweets_Collection(tweets_list, '30_days')


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
        return Tweets_Collection(tweets_list, 'archive')


    def _recent_api2(self, query: str, lang=None, since=None, until=None, max_results_for_page=100, number_pages=math.inf):
        if lang:
            query = query + f' lang:{lang}'
        if since:
            since = utils.conv_date_ISO(since)
        if until:
            until = utils.conv_date_ISO(until)
        tweets = []
        includes = {
            'users': [],
            'tweets': [],
            'media': []
        }
        for page in tw.Paginator(
            self.client.search_recent_tweets,
            query=query,
            end_time=until,
            start_time=since,
            max_results=max_results_for_page,
            sort_order='recency',
            expansions=fields['expansions'],
            media_fields=fields['media'],
            place_fields=fields['place'],
            tweet_fields=fields['tweet'],
            user_fields=fields['user'],
            limit=number_pages):

            tweets.extend(page.data)
            includes['users'].extend(page.includes['users'])
            includes['tweets'].extend(page.includes['tweets'])
            includes['media'].extend(page.includes['media'])

        return Tweets_Collection([tweets, includes], 'recent_apiV2')

    # def _archive_api2(self, query: str, lang=None, since=None, until=None, max_results_for_page=500, number_pages=math.inf):
    #     if lang:
    #         query = query + f' lang:{lang}'
    #     if since:
    #         since = utils.conv_date_ISO(since)
    #     if until:
    #         until = utils.conv_date_ISO(until)
    #     tweets = []
    #     includes = {
    #         'users': [],
    #         'tweets': [],
    #         'media': []
    #     }
    #     for page in tw.Paginator(
    #         self.client.search_all_tweets,
    #         query=query,
    #         end_time=until,
    #         start_time=since,
    #         max_results=max_results_for_page,
    #         sort_order='recency',
    #         expansions=fields['expansions'],
    #         media_fields=fields['media'],
    #         place_fields=fields['place'],
    #         tweet_fields=fields['tweet'],
    #         user_fields=fields['user'],
    #         limit=number_pages):

    #         tweets.extend(page.data)
    #         if 'users' in page.includes.keys():
    #             includes['users'].extend(page.includes['users'])
    #         if 'tweets' in page.includes.keys():
    #             includes['tweets'].extend(page.includes['tweets'])
    #         if 'media' in page.includes.keys():
    #             includes['media'].extend(page.includes['media'])
    #     return Tweets_Collection([tweets, includes], 'archive_apiV2')


    def _archive_api2(self, query: str, lang=None, since=None, until=None, max_results=math.inf):
        search_max_results = 500
        if max_results < 500:
            search_max_results = max_results
        if lang:
            query = query + f' lang:{lang}'
        if since:
            since = utils.conv_date_ISO(since)
        if until:
            until = utils.conv_date_ISO(until)
        tweets = []
        includes = {
            'users': [],
            'tweets': []
        }
        next_token = ''
        tweets_count = 0
        requests_count = 0
        start = time.time()
        while(True):
            request_start = time.time()
            if next_token == '':
                tts = self.client.search_all_tweets(
                    query=query,
                    end_time=until,
                    start_time=since,
                    max_results=search_max_results,
                    sort_order='recency',
                    expansions=fields['expansions'],
                    media_fields=fields['media'],
                    place_fields=fields['place'],
                    tweet_fields=fields['tweet'],
                    user_fields=fields['user']
                )
                tweets_count += len(tts.data)
                tweets.extend(tts.data)
                if 'users' in tts.includes.keys():
                    includes['users'].extend(tts.includes['users'])
                if 'tweets' in tts.includes.keys():
                    includes['tweets'].extend(tts.includes['tweets'])
                if 'next_token' in tts.meta.keys():
                    next_token = tts.meta['next_token']
                else:
                    break
                if tweets_count == max_results:
                    break
                request_end = time.time()
                requests_count += 1
                if requests_count == 300 and request_end - start < 900.0:
                    requests_count = 0
                    print(f'Limit rate reached. Sleeping for{request_end - start} seconds')
                    time.sleep(request_end - start)
                    start = time.time()
                if request_end - request_start < 1.0:
                    time.sleep(request_end - request_start)
            else:
                if not math.isinf(max_results) and tweets_count + search_max_results > max_results:
                    search_max_results = max_results - tweets_count
                    if search_max_results < 10:
                        search_max_results = 10
                    tts = self.client.search_all_tweets(
                        query=query,
                        end_time=until,
                        start_time=since,
                        max_results=search_max_results,
                        sort_order='recency',
                        expansions=fields['expansions'],
                        media_fields=fields['media'],
                        place_fields=fields['place'],
                        tweet_fields=fields['tweet'],
                        user_fields=fields['user']
                    )
                    tweets_count += len(tts.data)
                    tweets.extend(tts.data)
                    if 'users' in tts.includes.keys():
                        includes['users'].extend(tts.includes['users'])
                    if 'tweets' in tts.includes.keys():
                        includes['tweets'].extend(tts.includes['tweets'])
                    if 'next_token' in tts.meta.keys():
                        next_token = tts.meta['next_token']
                    else:
                        break
                    if tweets_count == max_results:
                        break
                    request_end = time.time()
                    requests_count += 1
                    if requests_count == 300 and request_end - start < 900.0:
                        requests_count = 0
                        print(f'Limit rate reached. Sleeping for{request_end - start} seconds')
                        time.sleep(request_end - start)
                        start = time.time()
                    if request_end - request_start < 1.0:
                        time.sleep(request_end - request_start)
                else:
                    tts = self.client.search_all_tweets(
                        query=query,
                        end_time=until,
                        start_time=since,
                        max_results=search_max_results,
                        sort_order='recency',
                        expansions=fields['expansions'],
                        media_fields=fields['media'],
                        place_fields=fields['place'],
                        tweet_fields=fields['tweet'],
                        user_fields=fields['user']
                    )
                    tweets_count += len(tts.data)
                    tweets.extend(tts.data)
                    if 'users' in tts.includes.keys():
                        includes['users'].extend(tts.includes['users'])
                    if 'tweets' in tts.includes.keys():
                        includes['tweets'].extend(tts.includes['tweets'])
                    if 'next_token' in tts.meta.keys():
                        next_token = tts.meta['next_token']
                    else:
                        break
                    if tweets_count == max_results:
                        break
                    request_end = time.time()
                    requests_count += 1
                    if requests_count == 300 and request_end - start < 900.0:
                        requests_count = 0
                        print(f'Limit rate reached. Sleeping for{request_end - start} seconds')
                        time.sleep(request_end - start)
                        start = time.time()
                    if request_end - request_start < 1.0:
                        time.sleep(request_end - request_start)
        return Tweets_Collection([tweets, includes], 'archive_apiV2')
