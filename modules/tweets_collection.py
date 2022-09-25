import pandas as pd

df_columns = [
    'created_at', 'tweet_id', 'tweet_content', 'user_info', 'media', 'urls',
    'user_mentions', 'reply_to', 'quoted_from', 'retweeted_from', 'hashtags'
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
        for column in df_columns:
            df_content[column] = []

        for tweet in self.tweets_json:
            is_retweet = True if 'retweeted_status' in tweet.keys() else False  # if it is a retweet
            df_content['created_at'].append(tweet['created_at'])                # created at
            df_content['tweet_id'].append(tweet['id'])                          # user id
            if is_retweet:                                                      # tweet textual content
                if self.search_type == 'recent':
                    df_content['tweet_content'].append(tweet['retweeted_status']['full_text'])
                else:
                    if tweet['retweeted_status']['truncated']:
                        df_content['tweet_content'].append(tweet['retweeted_status']['extended_tweet']['full_text'])
                    else:
                        df_content['tweet_content'].append(tweet['retweeted_status']['text'])
            elif tweet['truncated'] == True:
                df_content['tweet_content'].append(tweet['extended_tweet']['full_text'])
            elif self.search_type == 'recent':
                df_content['tweet_content'].append(tweet['full_text'])
            else:
                df_content['tweet_content'].append(tweet['text'])
            df_content['user_info'].append({                                    # user info
                'screen_name': tweet['user']['screen_name'],
                'name': tweet['user']['name'],
                'id': tweet['user']['id'],
                'description': tweet['user']['description'],
                'created_at': tweet['user']['created_at']
            })
            if 'media' not in tweet['entities'].keys() and not is_retweet:      # media
                df_content['media'].append(None)
            elif is_retweet and 'media' not in tweet['retweeted_status']['entities'].keys():
                df_content['media'].append(None)
            elif is_retweet and 'media' in tweet['retweeted_status']['entities'].keys():
                media_list = []
                for media in tweet['retweeted_status']['extended_entities']['media']:
                    media_list.append({
                        'type': media['type'],
                        'url': media['media_url']
                    })
                df_content['media'].append(media_list)
            else:
                media_list = []
                for media in tweet['extended_entities']['media']:
                    media_list.append({
                        'type': media['type'],
                        'url': media['media_url']
                    })
                df_content['media'].append(media_list)
            if is_retweet and tweet['retweeted_status']['entities']['urls']:    # urls
                url_list = []
                for url in tweet['retweeted_status']['entities']['urls']:
                    url_list.append(url['expanded_url'])
                df_content['urls'].append(url_list)
            elif tweet['entities']['urls']:
                url_list = []
                for url in tweet['entities']['urls']:
                    url_list.append(url['expanded_url'])
                df_content['urls'].append(url_list)
            else:
                df_content['urls'].append(None)
            if is_retweet:                                                      # retweet
                df_content['retweeted_from'].append({
                    'user': tweet['retweeted_status']['user']['screen_name'],
                    'user_id': tweet['retweeted_status']['user']['id'],
                    'tweet_id': tweet['retweeted_status']['id']
                })
            else:
                df_content['retweeted_from'].append(None)
            if tweet['in_reply_to_status_id'] == None and tweet['in_reply_to_user_id'] == None:
                df_content['reply_to'].append(None)
            else:
                df_content['reply_to'].append({
                    'user': tweet['in_reply_to_screen_name'],
                    'user_id': tweet['in_reply_to_user_id'],
                    'tweet_id': tweet['in_reply_to_status_id']
                })
            if 'quoted_status' in tweet.keys():
                if self.search_type == 'recent':                                # quote
                    df_content['quoted_from'].append({
                    'user': tweet['quoted_status']['user']['screen_name'],
                    'user_id': tweet['quoted_status']['user']['id'],
                    'tweet_id': tweet['quoted_status']['id'],
                    'quoted_content': tweet['quoted_status']['full_text']
                })
                else:
                    if tweet['quoted_status']['truncated']:
                        df_content['quoted_from'].append({
                        'user': tweet['quoted_status']['user']['screen_name'],
                        'user_id': tweet['quoted_status']['user']['id'],
                        'tweet_id': tweet['quoted_status']['id'],
                        'quoted_content': tweet['quoted_status']['extended_tweet']['full_text']
                    })
                    else:
                        df_content['quoted_from'].append({
                            'user': tweet['quoted_status']['user']['screen_name'],
                            'user_id': tweet['quoted_status']['user']['id'],
                            'tweet_id': tweet['quoted_status']['id'],
                            'quoted_content': tweet['quoted_status']['text']
                        })
            else:
                df_content['quoted_from'].append(None)
            if is_retweet:                                                      # hashtags
                if self.search_type == 'recent':
                    if tweet['retweeted_status']['entities']['hashtags']:
                        df_content['hashtags'].append(['#'+hashtag['text'] for hashtag in tweet['retweeted_status']['entities']['hashtags']])
                    else:
                        df_content['hashtags'].append(None)
                else:
                    if not tweet['retweeted_status']['truncated']:
                        if tweet['retweeted_status']['entities']['hashtags']:
                            df_content['hashtags'].append(['#'+hashtag['text'] for hashtag in tweet['retweeted_status']['entities']['hashtags']])
                        else:
                            df_content['hashtags'].append(None)
                    else:
                        if tweet['retweeted_status']['extended_tweet']['entities']['hashtags']:
                            df_content['hashtags'].append(['#'+hashtag['text'] for hashtag in tweet['retweeted_status']['extended_tweet']['entities']['hashtags']])
                        else:
                            df_content['hashtags'].append(None)
            elif tweet['entities']['hashtags'] and not tweet['truncated']:
                df_content['hashtags'].append(['#'+hashtag['text'] for hashtag in tweet['entities']['hashtags']])
            elif tweet['truncated'] and tweet['extended_tweet']['entities']['hashtags']:
                if tweet['extended_tweet']['entities']['hashtags']:
                    df_content['hashtags'].append(['#'+hashtag['text'] for hashtag in tweet['extended_tweet']['entities']['hashtags']])
            else:
                df_content['hashtags'].append(None)
            df_content['user_mentions'].append('0')

        return pd.DataFrame(df_content)
