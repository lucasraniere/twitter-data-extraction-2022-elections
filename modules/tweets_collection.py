import re
from weakref import ref
import pandas as pd
from datetime import datetime

columns = [
    'created_at', 'tweet_id', 'tweet_content', 'user', 'user_info', 'has_mention', 'native_mentions',
    'retweet_mentions', 'is_reply', 'reply_to', 'is_quote', 'quoted_from', 'is_retweet', 'retweeted_from',
    'hashtags'
]

columns_v2 = [
    'created_at', 'tweet_id', 'tweet_content', 'user', 'user_info', 'has_mention', 'mentions', 'is_reply',
    'reply_to', 'is_quote', 'quoted_from', 'is_retweet', 'retweeted_from', 'hashtags'
]

class Tweets_Collection:
    def __init__(self, tweets_list: list, search_type: str):
        self.tweets_json = tweets_list
        self.search_type = search_type
        if search_type!='recent_apiV2' and search_type!='archive_apiV2':
            self._amount =  len(tweets_list)
        else:
            self._amount = len(tweets_list[0])
        self._info = f'This collection contains {self._amount} tweets. Extraction method: {self.search_type}.'


    def get_tweets_dict(self):
        if self.search_type!='recent_apiV2' or self.search_type!='archive_apiV2':
            return self.tweets_json
        else:
            return  self.tweets_json[0], self.tweets_json[1]


    def check_includes_user(self, user_id: int):
        referenced_user = None
        for user in self.tweets_json[1]['users']:
            if user.id == user_id:
                referenced_user = user
                break
        return referenced_user


    def check_includes_tweet(self, tweet_id: int):
        referenced_tweet = None
        for tweet in self.tweets_json[1]['tweets']:
            if tweet.id == tweet_id:
                referenced_tweet = tweet
                break
        return referenced_tweet


    def get_dataframe(self):
        df_content = {}
        if self.search_type=='recent' or self.search_type=='archive' or self.search_type=='30_days':
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
        else:
            for column in columns_v2:
                df_content[column] = []
            tweet_data = self.tweets_json[0]
            tweet_includes = self.tweets_json[1]
            for tweet in tweet_data:
                has_ref = True if 'referenced_tweets' in tweet.data.keys() else False
                is_retweet = False
                is_quoted = False
                is_reply = False
                referenced_retweet = None
                referenced_quoted = None
                referenced_reply = None
                if has_ref:
                    for referenced_tt in tweet.referenced_tweets:
                        if referenced_tt.type == 'retweeted':
                            is_retweet = True
                            referenced_retweet = referenced_tt.id
                        elif referenced_tt.type == 'quoted':
                            is_quoted = True
                            referenced_quoted = referenced_tt.id
                        elif referenced_tt.type == 'replied_to':
                            is_reply = True
                            referenced_reply = referenced_tt.id
                df_content['created_at'].append(tweet.created_at.strftime('%Y-%m-%d %H:%M:%S'))
                df_content['tweet_id'].append(tweet.id)
                for user in tweet_includes['users']:
                    if user.id == tweet.author_id:
                        df_content['user'].append(user.username)
                        df_content['user_info'].append({
                            'id': user.id,
                            'name': user.name,
                            'description': user.description,
                            'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                            'public_metrics': user.public_metrics
                        })
                        break
                df_content['is_reply'].append(is_reply)
                df_content['is_quote'].append(is_quoted)
                df_content['is_retweet'].append(is_retweet)
                if is_retweet:
                    ref_tweet = self.check_includes_tweet(referenced_retweet)
                    if ref_tweet:
                        ref_user = self.check_includes_user(ref_tweet.author_id)
                        if ref_user:
                            df_content['retweeted_from'].append({
                                'user': ref_user.username,
                                'user_id': ref_user.id,
                                'tweet_content': ref_tweet.text,
                                'tweet_id': ref_tweet.id
                            })
                        else:
                            df_content['retweeted_from'].append({
                                'user': None,
                                'user_id': None,
                                'tweet_content': ref_tweet.text,
                                'tweet_id': ref_tweet.id
                            })
                        df_content['tweet_content'].append(ref_tweet.text)
                        if 'entities' in ref_tweet.data.keys():
                            if 'hashtags' in ref_tweet.entities.keys():
                                df_content['hashtags'].append(['#'+hashtag['tag'] for hashtag in ref_tweet.entities['hashtags']])
                            else:
                                df_content['hashtags'].append(None)
                            if 'mentions' in ref_tweet.entities.keys():
                                df_content['has_mention'].append(True)
                                df_content['mentions'].append([{'id':mention['id'],'username':mention['username']} for mention in ref_tweet.entities['mentions']])
                            else:
                                df_content['has_mention'].append(False)
                                df_content['mentions'].append(None)
                        else:
                            df_content['hashtags'].append(None)
                            df_content['has_mention'].append(False)
                            df_content['mentions'].append(None)
                    else:
                        df_content['retweeted_from'].append('NOT AVAILABLE')
                        df_content['tweet_content'].append(tweet.text)
                        if 'entities' in tweet.data.keys():
                            if 'hashtags' in tweet.entities.keys():
                                df_content['hashtags'].append(['#'+hashtag['tag'] for hashtag in tweet.entities['hashtags']])
                            else:
                                df_content['hashtags'].append(None)
                            if 'mentions' in tweet.entities.keys():
                                df_content['has_mention'].append(True)
                                df_content['mentions'].append([{'id':mention['id'],'username':mention['username']} for mention in tweet.entities['mentions']])
                            else:
                                df_content['has_mention'].append(False)
                                df_content['mentions'].append(None)
                        else:
                            df_content['hashtags'].append(None)
                            df_content['has_mention'].append(False)
                            df_content['mentions'].append(None)
                else:
                    df_content['retweeted_from'].append(None)
                    df_content['tweet_content'].append(tweet.text)
                    if 'entities' in tweet.data.keys():
                        if 'hashtags' in tweet.entities.keys():
                            df_content['hashtags'].append(['#'+hashtag['tag'] for hashtag in tweet.entities['hashtags']])
                        else:
                            df_content['hashtags'].append(None)
                        if 'mentions' in tweet.entities.keys():
                            df_content['has_mention'].append(True)
                            df_content['mentions'].append([{'id':mention['id'],'username':mention['username']} for mention in tweet.entities['mentions']])
                        else:
                            df_content['has_mention'].append(False)
                            df_content['mentions'].append(None)
                    else:
                        df_content['hashtags'].append(None)
                        df_content['has_mention'].append(False)
                        df_content['mentions'].append(None)
                if is_quoted:
                    ref_tweet = self.check_includes_tweet(referenced_quoted)
                    if ref_tweet:
                        ref_user = self.check_includes_user(ref_tweet.author_id)
                        if ref_user:
                            df_content['quoted_from'].append({
                                'user': ref_user.username,
                                'user_id': ref_user.id,
                                'tweet_content': ref_tweet.text,
                                'tweet_id': ref_tweet.id
                            })
                        else:
                            df_content['quoted_from'].append({
                                'user': None,
                                'user_id': None,
                                'tweet_content': ref_tweet.text,
                                'tweet_id': ref_tweet.id
                            })
                    else:
                        df_content['quoted_from'].append('NOT AVAILABLE')
                else:
                    df_content['quoted_from'].append(None)
                if is_reply:
                    ref_tweet = self.check_includes_tweet(referenced_reply)
                    if ref_tweet:
                        ref_user = self.check_includes_user(ref_tweet.author_id)
                        if ref_user:
                            df_content['reply_to'].append({
                                'user': ref_user.username,
                                'user_id': ref_user.id,
                                'tweet_content': ref_tweet.text,
                                'tweet_id': ref_tweet.id
                            })
                        else:
                            df_content['reply_to'].append({
                                'user': None,
                                'user_id': None,
                                'tweet_content': ref_tweet.text,
                                'tweet_id': ref_tweet.id
                            })
                    else:
                        df_content['reply_to'].append('NOT AVAILABLE')
                else:
                    df_content['reply_to'].append(None)
        return pd.DataFrame(df_content)
