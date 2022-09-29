from operator import is_
import pandas as pd

columns = [
    'created_at', 'tweet_id', 'tweet_content', 'user', 'user_info', 'has_mention', 'native_mentions',
    'retweet_mentions', 'is_reply', 'reply_to', 'is_quote', 'quoted_from', 'is_retweet', 'retweeted_from',
    'hashtags'
]

class Tweets_Collection:
    def __init__(self, tweets_list: list, search_type: str):
        self.tweets_json = tweets_list
        self.search_type = search_type
        self._amount = len(tweets_list)
        self._info = f'This collection contains {self._amount} tweets. Extraction method: {self.search_type}.'


    def get_tweets_dict(self):
        return self.tweets_json


    def get_dataframe(self):
        df_content = {}
        for column in columns:
            df_content[column] = []

        for tweet in self.tweets_json:
            native_mentions = False
            retweet_mentions = False
            is_retweet = False
            if 'retweeted_status' in tweet.keys():                                                                                  # retweeted from
                is_retweet = True
                df_content['retweeted_from'].append({
                    'user': tweet['retweeted_status']['user']['screen_name'],
                    'user_id': tweet['retweeted_status']['user']['id'],
                    'tweet_id': tweet['retweeted_status']['id']
                })
            else:
                df_content['retweeted_from'].append(None)

            is_quoted = True if 'quoted_status' in tweet.keys() else False
            is_reply = True if not is_retweet and tweet['in_reply_to_status_id'] else False

            df_content['created_at'].append(tweet['created_at'])                                                                    # created at
            df_content['tweet_id'].append(tweet['id'])                                                                              # tweet id
            df_content['user'].append(tweet['user']['screen_name'])                                                                 # user screen name
            df_content['user_info'].append({                                                                                        # user info
                'name': tweet['user']['name'],
                'id': tweet['user']['id'],
                'description': tweet['user']['description'],
                'created_at': tweet['user']['created_at']
            })
            df_content['is_reply'].append(is_reply)                                                                                 # is reply?
            df_content['is_quote'].append(is_quoted)                                                                                # is quoted retweet?
            df_content['is_retweet'].append(is_retweet)                                                                             # is retweet?

            if is_reply:                                                                                                            # reply to
                df_content['reply_to'].append({
                    'user': tweet['in_reply_to_screen_name'],
                    'user_id': tweet['in_reply_to_user_id'],
                    'status_id': tweet['in_reply_to_status_id']
                })
            else:
                df_content['reply_to'].append(None)

            if self.search_type == 'recent':                                                                                        # if is recent search
                if is_retweet:                                                                                                          # if is retweet
                    df_content['tweet_content'].append(tweet['retweeted_status']['full_text'])                                              # tweet content
                    if tweet['retweeted_status']['entities']['hashtags']:                                                                   # hashtags
                        hashtag_list = ['#'+hashtag['text'] for hashtag in tweet['retweeted_status']['entities']['hashtags']]
                        df_content['hashtags'].append(hashtag_list)
                    else:
                        df_content['hashtags'].append(None)
                    df_content['native_mentions'].append(None)                                                                              # native mentions
                    if tweet['retweeted_status']['entities']['user_mentions']:                                                              # retweet mentions
                        retweet_mentions = True
                        mention_list = []
                        for mention in tweet['retweeted_status']['entities']['user_mentions']:
                            mention_list.append({
                                'user': mention['screen_name'],
                                'user_id': mention['id']
                            })
                        df_content['retweet_mentions'].append(mention_list)
                    else:
                        df_content['retweet_mentions'].append(None)
                else:                                                                                                                   # if isn't retweet
                    df_content['tweet_content'].append(tweet['full_text'])                                                                  # tweet content
                    if tweet['entities']['hashtags']:                                                                                       # hashtags
                        hashtag_list = ['#'+hashtag['text'] for hashtag in tweet['entities']['hashtags']]
                        df_content['hashtags'].append(hashtag_list)
                    else:
                        df_content['hashtags'].append(None)
                    df_content['retweet_mentions'].append(None)                                                                             # retweet mentions
                    if tweet['entities']['user_mentions']:                                                                                  # native mentions
                        native_mentions = True
                        mention_list = []
                        for mention in tweet['entities']['user_mentions']:
                            mention_list.append({
                                'user': mention['screen_name'],
                                'user_id': mention['id']
                            })
                        df_content['native_mentions'].append(mention_list)
                    else:
                        df_content['native_mentions'].append(None)
                if is_quoted:                                                                                                           # quoted from
                    df_content['quoted_from'].append({
                        'user': tweet['quoted_status']['user']['screen_name'],
                        'user_id': tweet['quoted_status']['user']['id'],
                        'tweet_content': tweet['quoted_status']['full_text'],
                        'tweet_id': tweet['quoted_status']['id']
                    })
                else:
                    df_content['quoted_from'].append(None)
            else:                                                                                                                   # if is 30 days/archive
                if is_retweet:                                                                                                          # if is retweeted
                    df_content['native_mentions'].append(None)                                                                              # native mentions
                    if tweet['retweeted_status']['truncated']:                                                                              # if truncated
                        df_content['tweet_content'].append(tweet['retweeted_status']['extended_tweet']['full_text'])                             # tweet content
                        if tweet['retweeted_status']['extended_tweet']['entities']['hashtags']:                                                 # hashtags
                            hashtag_list = ['#'+hashtag['text'] for hashtag in tweet['retweeted_status']['extended_tweet']['entities']['hashtags']]
                            df_content['hashtags'].append(hashtag_list)
                        else:
                            df_content['hashtags'].append(None)
                        if tweet['retweeted_status']['extended_tweet']['entities']['user_mentions']:                                            # retweet mentions
                            retweet_mentions = True
                            mention_list = []
                            for mention in tweet['retweeted_status']['extended_tweet']['entities']['user_mentions']: 
                                mention_list.append({
                                    'user': mention['screen_name'],
                                    'id': mention['id']
                                })
                            df_content['retweet_mentions'].append(mention_list)
                        else:
                            df_content['retweet_mentions'].append(None)
                    else:                                                                                                                   # if isn't truncated
                        df_content['tweet_content'].append(tweet['retweeted_status']['text'])                                                    # tweet content
                        if tweet['retweeted_status']['entities']['hashtags']:                                                                   # hashtags
                            hashtag_list = ['#'+hashtag['text'] for hashtag in tweet['retweeted_status']['entities']['hashtags']]
                            df_content['hashtags'].append(hashtag_list)
                        else:
                            df_content['hashtags'].append(None)
                        if tweet['retweeted_status']['entities']['user_mentions']:                                                              # retweet mentions
                            retweet_mentions = True
                            mention_list = []
                            for mention in tweet['retweeted_status']['entities']['user_mentions']:
                                mention_list.append({
                                    'user': mention['screen_name'],
                                    'id': mention['id']
                                })
                            df_content['retweet_mentions'].append(mention_list)
                        else:
                            df_content['retweet_mentions'].append(None)
                else:                                                                                                                   # if isn't retweet
                    df_content['retweet_mentions'].append(None)                                                                           # retweeted mentions
                    if tweet['truncated']:                                                                                                  # if truncated
                        df_content['tweet_content'].append(tweet['extended_tweet']['full_text'])                                                # tweet content
                        if tweet['extended_tweet']['entities']['hashtags']:                                                                     # hashatags
                            hashtag_list = ['#'+hashtag['text'] for hashtag in tweet['extended_tweet']['entities']['hashtags']]
                            df_content['hashtags'].append(hashtag_list)
                        else:
                            df_content.append(None)
                        if tweet['extended_tweet']['entities']['user_mentions']:                                                                # native mentions
                            native_mentions = True
                            mention_list = []
                            for mention in tweet['extended_tweet']['entities']['user_mentions']:
                                mention_list.append({
                                    'user': mention['screen_name'],
                                    'id': mention['id']
                                })
                            df_content['native_mentions'].append(mention_list)
                        else:
                            df_content['native_mentions'].append(None)
                    else:                                                                                                                   # if isnt truncated
                        df_content['tweet_content'].append(tweet['text'])                                                                       # tweet content
                        if tweet['entities']['hashtags']:                                                                                       # hashtags
                            hashtag_list = ['#'+hashtag['text'] for hashtag in tweet['entities']['hashtags']]
                            df_content['hashtags'].append(hashtag_list)
                        else:
                            df_content['hashtags'].append(None)
                        if tweet['entities']['user_mentions']:                                                                                  # native mentions
                            native_mentions = True
                            mention_list = []
                            for mention in tweet['entities']['user_mentions']:
                                mention_list.append({
                                    'user': mention['screen_name'],
                                    'id': mention['id']
                                })
                            df_content['native_mentions'].append(mention_list)
                        else:
                            df_content['native_mentions'].append(None)
                if is_quoted:                                                                                                           # quoted from
                    if tweet['quoted_status']['truncated']:
                        df_content['quoted_from'].append({
                            'user': tweet['quoted_status']['user']['screen_name'],
                            'user_id': tweet['quoted_status']['user']['id'],
                            'tweet_content': tweet['quoted_status']['extended_tweet']['full_text'],
                            'tweet_id': tweet['quoted_status']['id']
                        })
                    else:
                        df_content['quoted_from'].append({
                            'user': tweet['quoted_status']['user']['screen_name'],
                            'user_id': tweet['quoted_status']['user']['id'],
                            'tweet_content': tweet['quoted_status']['text'],
                            'tweet_id': tweet['quoted_status']['id']
                        })
                else:
                    df_content['quoted_from'].append(None)
            df_content['has_mention'].append(True if native_mentions or retweet_mentions else False)                                    # has mentions
        return pd.DataFrame(df_content)
