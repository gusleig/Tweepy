import tweepy
import pandas as pd
import json
import datetime
import time

# Add your credentials here
'''
twitter_keys = {
        'consumer_key':        "l8mlHCL3xHgqnh9UC4kuojDYj",
        'consumer_secret':     "8I6plO3k7H6Kzah6QvMaAbHb5cwqPNa3y6hBVqnhrXAgSyBTZT",
        'access_token_key':    "9138172-TY5wut9KG8Hh9uDEk3vdSsxOUqy6FPOEfFrCdvbFNY",
        'access_token_secret': "XhMxteVWWMT4ktWKebLnw0II1WVkLARgFcIC5PgWlZ11R"
    }

# Authenticate to Twitter
auth = tweepy.OAuthHandler(twitter_keys['consumer_key'], twitter_keys['consumer_secret'])
auth.set_access_token(twitter_keys['access_token_key'], twitter_keys['access_token_secret'])

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
# test authentication
try:
    api.verify_credentials()
    print("Authentication OK")
except Exception as e:
    print("Error during authentication, %s" % e)

'''


class TweetMiner(object):
    result_limit = 20
    data = []
    api = False

    twitter_keys = {
        'consumer_key': "l8mlHCL3xHgqnh9UC4kuojDYj",
        'consumer_secret': "8I6plO3k7H6Kzah6QvMaAbHb5cwqPNa3y6hBVqnhrXAgSyBTZT",
        'access_token_key': "9138172-TY5wut9KG8Hh9uDEk3vdSsxOUqy6FPOEfFrCdvbFNY",
        'access_token_secret': "XhMxteVWWMT4ktWKebLnw0II1WVkLARgFcIC5PgWlZ11R"
    }

    def __init__(self, keys_dict=twitter_keys, api=api, result_limit=20):

        self.twitter_keys = keys_dict

        auth = tweepy.OAuthHandler(keys_dict['consumer_key'], keys_dict['consumer_secret'])
        auth.set_access_token(keys_dict['access_token_key'], keys_dict['access_token_secret'])

        self.api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        self.twitter_keys = keys_dict

        self.result_limit = result_limit

    def mine_search(self, query, max_pages=5, lang='*', geocode='', result_type="mixed", dateuntil=''):
        # You can only set your query string to '*'
        # when also using the geocode parameter. A search for q='*' without a specified geocode is invalid.

        data = []
        last_tweet_id = False
        page = 1
        max_tweets = 150

        while page <= max_pages:

            # tweets = tweepy.Cursor(self.api.search, q=query, geocode=geocode, count=100).items(max_tweets)

            # tweets_list = [[tweet.text, tweet.created_at, tweet.id_str, tweet.favorite_count, tweet.user.screen_name,
            #                tweet.user.id_str, tweet.user.location, tweet.user.followers_count, tweet.coordinates,
            #                tweet.place] for tweet in tweets]

            statuses = self.api.search(q=query,
                            lang=lang,
                            rpp=5,
                            geocode=geocode,
                            result_type=result_type,
                            until=dateuntil)

            for item in statuses:

                mined = {
                    'tweet_id': item.id,
                    'name': item.user.name,
                    'screen_name': item.user.screen_name,
                    'retweet_count': item.retweet_count,
                    'text': item.text,
                    'mined_at': datetime.datetime.now(),
                    'created_at': item.created_at,
                    'favourite_count': item.favorite_count,
                    'hashtags': item.entities['hashtags'],
                    'status_count': item.user.statuses_count,
                    'location': item.place,
                    'source_device': item.source
                }

                try:
                    mined['retweet_text'] = item.retweeted_status.text
                except:
                    mined['retweet_text'] = 'None'

                try:
                    mined['quote_text'] = item.quoted_status.full_text
                    mined['quote_screen_name'] = item.quoted_status.user.screen_name
                except:
                    mined['quote_text'] = 'None'
                    mined['quote_screen_name'] = 'None'

                last_tweet_id = item.id
                data.append(mined)

            page += 1

        return data

    def mine_user_tweets(self, user="dril",  # BECAUSE WHO ELSE!
                         mine_rewteets=False,
                         max_pages=5):

        data = []
        last_tweet_id = False
        page = 1

        while page <= max_pages:
            if last_tweet_id:
                statuses = self.api.user_timeline(screen_name=user,
                                                  count=self.result_limit,
                                                  max_id=last_tweet_id - 1,
                                                  tweet_mode='extended',
                                                  include_retweets=True
                                                  )
            else:
                statuses = self.api.user_timeline(screen_name=user,
                                                  count=self.result_limit,
                                                  tweet_mode='extended',
                                                  include_retweets=True)

            for item in statuses:

                mined = {
                    'tweet_id': item.id,
                    'name': item.user.name,
                    'screen_name': item.user.screen_name,
                    'retweet_count': item.retweet_count,
                    'text': item.full_text,
                    'mined_at': datetime.datetime.now(),
                    'created_at': item.created_at,
                    'favourite_count': item.favorite_count,
                    'hashtags': item.entities['hashtags'],
                    'status_count': item.user.statuses_count,
                    'location': item.place,
                    'source_device': item.source
                }

                try:
                    mined['retweet_text'] = item.retweeted_status.full_text
                except:
                    mined['retweet_text'] = 'None'

                try:
                    mined['quote_text'] = item.quoted_status.full_text
                    mined['quote_screen_name'] = item.quoted_status.user.screen_name
                except:
                    mined['quote_text'] = 'None'
                    mined['quote_screen_name'] = 'None'

                last_tweet_id = item.id
                data.append(mined)

            page += 1

        return data


def get_timeline():
    public_tweets = api.home_timeline()
    for tweet in public_tweets:
        print(tweet.text)

    status = public_tweets[0]

    # convert to string
    json_str = json.dumps(status._json)

    # deserialise string into python object
    parsed = json.loads(json_str)

    print(json.dumps(parsed, indent=4, sort_keys=True))


def get_search(query):
    api.search(q=query, lang="en", rpp=5)


def get_timeline2(user_id):
    timeline = api.user_timeline(user_id=user_id, count=200)


def get_followers(screen_name):
    api.followers_ids(screen_name=screen_name)


def get_ids(screen_name):
    '''
    :argument: screen_name of user
    :returns: a list_id of the given user's followers
    '''
    # get first list
    first_list = api.followers_ids(screen_name=screen_name)
    id_list = first_list['ids']
    cursor = first_list['next_cursor']
    while cursor != 0:
        user_ids = api.followers_ids(screen_name=screen_name,  cursor=cursor)
        id_list.extend(user_ids[0]['ids'])
        cursor = user_ids[0]['next_cursor']
    return id_list


if __name__ == '__main__':

    miner = TweetMiner(result_limit=200)
    # mined_tweets = miner.mine_user_tweets(user='dril', max_pages=17)

    geocode = "-22.9138851,-43.7261746, 5mi"
    result_type = "recent"
    dateuntil = time.strftime('%Y-%m-%d', time.localtime())
    lang = 'pt'
    query = "corona"

    mined_tweets = miner.mine_search(query, max_pages=20, result_type=result_type, lang='en')

    mined_tweets_df = pd.DataFrame(mined_tweets)

    print(mined_tweets_df)
