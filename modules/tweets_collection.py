from operator import is_
import pandas as pd

columns = [
    'created_at', 'tweet_id', 'tweet_content', 'user', 'user_info', 'has_mention', 'has_hard_mention',
    'mentions', 'hard_mentions', 'is_reply', 'reply_to', 'is_quote', 'quoted_from', 'is_retweet',
    'retweeted_from', 'hashtags'
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
                else:                                                                                                                   # if isn't retweet
                    df_content['tweet_content'].append(tweet['full_text'])                                                                  # tweet content
                    if tweet['entities']['hashtags']:                                                                                       # hashtags
                        hashtag_list = ['#'+hashtag['text'] for hashtag in tweet['entities']['hashtags']]
                        df_content['hashtags'].append(hashtag_list)
                    else:
                        df_content['hashtags'].append(None)
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
                    if tweet['retweeted_status']['truncated']:                                                                              # if truncated
                        df_content['text_content'].append(tweet['retweeted_status']['extended_tweet']['full_text'])                             # tweet content
                        if tweet['retweeted_status']['extended_tweet']['entities']['hashtags']:                                                 # hashtags
                            hashtag_list = ['#'+hashtag['text'] for hashtag in tweet['retweeted_status']['extended_tweet']['entities']['hashtags']]
                            df_content['hashtags'].append(hashtag_list)
                        else:
                            df_content['hashtags'].append(None)
                    else:                                                                                                                   # if isn't truncated
                        df_content['text_content'].append(tweet['retweeted_status']['text'])                                                    # tweet content
                        if tweet['retweeted_status']['entities']['hashtags']:                                                                   # hashtags
                            hashtag_list = ['#'+hashtag['text'] for hashtag in tweet['retweeted_status']['entities']['hashtags']]
                            df_content['hashtags'].append(hashtag_list)
                        else:
                            df_content['hashtags'].append(None)
                else:                                                                                                                   # if isn't retweet
                    if tweet['truncated']:                                                                                                  # if truncated
                        df_content['tweet_content'].append(tweet['extended_tweet']['full_text'])                                                # tweet content
                        if tweet['extended_tweet']['entities']['hashtags']:                                                                     # hashatags
                            hashtag_list = ['#'+hashtag['text'] for hashtag in tweet['extended_tweet']['entities']['hashtags']]
                            df_content['hashtags'].append(hashtag_list)
                        else:
                            df_content.append(None)
                    else:                                                                                                                   # if isnt truncated
                        df_content['tweet_content'].append(tweet['text'])                                                                       # tweet content
                        if tweet['entities']['hashtags']:                                                                                       # hashtags
                            hashtag_list = ['#'+hashtag for hashtag in tweet['entities']['hashtags']]
                            df_content['hashtags'].append(hashtag_list)
                        else:
                            df_content['hashtags'].append(None)
                if is_quoted:                                                                                                                   # quoted from
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



        # for tweet in self.tweets_json:
            # is_retweet = True if 'retweeted_status' in tweet.keys() else False  # if it is a retweet
            # df_content['created_at'].append(tweet['created_at'])                # created at
            # df_content['tweet_id'].append(tweet['id'])                          # user id
            # if is_retweet:                                                      # tweet textual content
            #     if self.search_type == 'recent':
            #         df_content['tweet_content'].append(tweet['retweeted_status']['full_text'])
            #     else:
            #         if tweet['retweeted_status']['truncated']:
            #             df_content['tweet_content'].append(tweet['retweeted_status']['extended_tweet']['full_text'])
            #         else:
            #             df_content['tweet_content'].append(tweet['retweeted_status']['text'])
            # elif tweet['truncated'] == True:
            #     df_content['tweet_content'].append(tweet['extended_tweet']['full_text'])
            # elif self.search_type == 'recent':
            #     df_content['tweet_content'].append(tweet['full_text'])
            # else:
            #     df_content['tweet_content'].append(tweet['text'])
            # df_content['user_info'].append({                                    # user info
            #     'screen_name': tweet['user']['screen_name'],
            #     'name': tweet['user']['name'],
            #     'id': tweet['user']['id'],
            #     'description': tweet['user']['description'],
            #     'created_at': tweet['user']['created_at']
            # })
            # if 'media' not in tweet['entities'].keys() and not is_retweet:      # media
            #     df_content['media'].append(None)
            # elif is_retweet and 'media' not in tweet['retweeted_status']['entities'].keys():
            #     df_content['media'].append(None)
            # elif is_retweet and 'media' in tweet['retweeted_status']['entities'].keys():
            #     media_list = []
            #     for media in tweet['retweeted_status']['extended_entities']['media']:
            #         media_list.append({
            #             'type': media['type'],
            #             'url': media['media_url']
            #         })
            #     df_content['media'].append(media_list)
            # else:
            #     media_list = []
            #     for media in tweet['extended_entities']['media']:
            #         media_list.append({
            #             'type': media['type'],
            #             'url': media['media_url']
            #         })
            #     df_content['media'].append(media_list)
            # if is_retweet and tweet['retweeted_status']['entities']['urls']:    # urls
            #     url_list = []
            #     for url in tweet['retweeted_status']['entities']['urls']:
            #         url_list.append(url['expanded_url'])
            #     df_content['urls'].append(url_list)
            # elif tweet['entities']['urls']:
            #     url_list = []
            #     for url in tweet['entities']['urls']:
            #         url_list.append(url['expanded_url'])
            #     df_content['urls'].append(url_list)
            # else:
            #     df_content['urls'].append(None)
            # if is_retweet:                                                      # retweet
            #     df_content['retweeted_from'].append({
            #         'user': tweet['retweeted_status']['user']['screen_name'],
            #         'user_id': tweet['retweeted_status']['user']['id'],
            #         'tweet_id': tweet['retweeted_status']['id']
            #     })
            # else:
            #     df_content['retweeted_from'].append(None)
            # if tweet['in_reply_to_status_id'] == None and tweet['in_reply_to_user_id'] == None:
            #     df_content['reply_to'].append(None)
            # else:
            #     df_content['reply_to'].append({
            #         'user': tweet['in_reply_to_screen_name'],
            #         'user_id': tweet['in_reply_to_user_id'],
            #         'tweet_id': tweet['in_reply_to_status_id']
            #     })
            # if 'quoted_status' in tweet.keys():
            #     if self.search_type == 'recent':                                # quote
            #         df_content['quoted_from'].append({
            #         'user': tweet['quoted_status']['user']['screen_name'],
            #         'user_id': tweet['quoted_status']['user']['id'],
            #         'tweet_id': tweet['quoted_status']['id'],
            #         'quoted_content': tweet['quoted_status']['full_text']
            #     })
            #     else:
            #         if tweet['quoted_status']['truncated']:
            #             df_content['quoted_from'].append({
            #             'user': tweet['quoted_status']['user']['screen_name'],
            #             'user_id': tweet['quoted_status']['user']['id'],
            #             'tweet_id': tweet['quoted_status']['id'],
            #             'quoted_content': tweet['quoted_status']['extended_tweet']['full_text']
            #         })
            #         else:
            #             df_content['quoted_from'].append({
            #                 'user': tweet['quoted_status']['user']['screen_name'],
            #                 'user_id': tweet['quoted_status']['user']['id'],
            #                 'tweet_id': tweet['quoted_status']['id'],
            #                 'quoted_content': tweet['quoted_status']['text']
            #             })
            # else:
            #     df_content['quoted_from'].append(None)
            # if is_retweet:                                                      # hashtags
            #     if self.search_type == 'recent':
            #         if tweet['retweeted_status']['entities']['hashtags']:
            #             df_content['hashtags'].append(['#'+hashtag['text'] for hashtag in tweet['retweeted_status']['entities']['hashtags']])
            #         else:
            #             df_content['hashtags'].append(None)
            #     else:
            #         if not tweet['retweeted_status']['truncated']:
            #             if tweet['retweeted_status']['entities']['hashtags']:
            #                 df_content['hashtags'].append(['#'+hashtag['text'] for hashtag in tweet['retweeted_status']['entities']['hashtags']])
            #             else:
            #                 df_content['hashtags'].append(None)
            #         else:
            #             if tweet['retweeted_status']['extended_tweet']['entities']['hashtags']:
            #                 df_content['hashtags'].append(['#'+hashtag['text'] for hashtag in tweet['retweeted_status']['extended_tweet']['entities']['hashtags']])
            #             else:
            #                 df_content['hashtags'].append(None)
            # elif tweet['entities']['hashtags'] and not tweet['truncated']:
            #     df_content['hashtags'].append(['#'+hashtag['text'] for hashtag in tweet['entities']['hashtags']])
            # elif tweet['truncated'] and tweet['extended_tweet']['entities']['hashtags']:
            #     if tweet['extended_tweet']['entities']['hashtags']:
            #         df_content['hashtags'].append(['#'+hashtag['text'] for hashtag in tweet['extended_tweet']['entities']['hashtags']])
            # else:
            #     df_content['hashtags'].append(None)
            # df_content['user_mentions'].append('0')
            # df_content['hard_mentions'].append('0')

        return pd.DataFrame(df_content)
