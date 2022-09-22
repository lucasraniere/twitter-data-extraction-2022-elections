import pandas as pd

class Tweets_Collection:
    def __init__(self, tweets_list: list):
        self.tweets_json = tweets_list
        self._amount = len(tweets_list)
        self._info = f'This collection contains {self._amount} tweets.'

    df_columns = [
        'created_at', 'tweet_id', 'tweet_content', 'user_info', 'tweet_metadata',
        'user_mentions', 'media', 'is_reply', 'reply_to', 'is_quoted', 'quoted_from',
        'is_retweet', 'retweeted_from', 'hashtags'
    ]

    def get_tweets_dict(self):
        return self.tweets_json

    def get_dataframe(self):
        pass
