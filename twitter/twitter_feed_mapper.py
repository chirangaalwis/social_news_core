#!/usr/bin/python3

import os, sys
from datetime import datetime
import math
import re
from json import JSONDecodeError
from pytrends.request import ResponseError, RateLimitError
from retrying import retry

from collections import OrderedDict

from twitter_client import get_twitter_client
from twitter_text_analyzer import refine_tweet_text, refine_hashtag

# time zone
from pytz import reference

sys.path.insert(0, os.path.realpath('..'))
from google_trends_client import get_pytrends
from models import SocialNetworkStatus, ZScore


def get_user_timeline_feed(client, username):
    # capture the optional id value of the tweet since which tweets are to be returned
    last_id = None
    ids = _load_latest_status_ids()
    if ('user_timeline' in ids):
        last_id = ids['user_timeline']

    # load tweets from user timeline
    if last_id is None:
        tweets = client.user_timeline(screen_name=username, count=30)
    else:
        tweets = client.user_timeline(screen_name=username, since_id=last_id)

    # convert tweets to application specific status objects
    statuses = _convert_tweets_to_native_statuses(tweets)

    if len(statuses) > 0:
        _update_latest_status_ids('user_timeline', statuses[0].id)

    return statuses


def get_bookmarks_feed(client, username, **optional):
    # capture the optional id value of the tweet since which tweets are to be returned
    last_id = None
    ids = _load_latest_status_ids()
    if ('bookmarks' in ids):
        last_id = ids['bookmarks']

    # load tweets from favorites
    if last_id is None:
        tweets = client.favorites(screen_name=username, count=30)
    else:
        tweets = client.favorites(screen_name=username, since_id=last_id)

    # convert tweets to application specific status objects
    statuses = _convert_tweets_to_native_statuses(tweets)

    if len(statuses) > 0:
        _update_latest_status_ids('bookmarks', statuses[0].id)

    return statuses


def get_followings_feed(client, username):
    tweets = client.home_timeline(screen_name=username, count=50)

    # convert tweets to application specific status objects
    statuses = _convert_tweets_to_native_statuses(tweets)

    return statuses


def get_public_trends_feed(client, **coordinates):
    # get world trends
    global_woeid = 1
    world_trends = _get_twitter_trends(client, global_woeid)

    if (('latitude' in coordinates) & ('longitude' in coordinates)):
        # get local trends
        response_data = client.trends_closest(coordinates['latitude'], coordinates['longitude'])
        locality_woeid = response_data[0]['woeid']
        local_trends = _get_twitter_trends(client, locality_woeid)

        merged_trends = list(set(world_trends) | set(local_trends))
        return merged_trends
    else:
        return world_trends


# support functions
def _convert_tweets_to_native_statuses(tweets):
    statuses = []

    for tweet in tweets:
        statuses.append(SocialNetworkStatus(native_identifier=tweet.id, text=refine_tweet_text(tweet.text),
                                            created=str(tweet.created_at), score=_generate_tweet_score(tweet)))

    return statuses


def _load_latest_status_ids():
    file_name = "since_ids.txt"
    file_path = os.path.realpath('.') + '/' + file_name

    ids = dict()

    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            for line in file:
                if ":" in line:
                    content = re.split('[:]', line)
                    ids[content[0]] = content[1].strip('\n')

    return ids


def _update_latest_status_ids(key, value):
    file_name = "since_ids.txt"
    file_path = os.path.realpath('.') + '/' + file_name

    ids = _load_latest_status_ids()

    ids[key] = value
    with open(file_path, 'w+') as file:
        for key, value in ids.items():
            file.write(key + ":" + str(value) + "\n")


def _generate_tweet_score(tweet):
    starting_score = 100
    starting_score = starting_score + (10 * tweet.retweet_count)
    starting_score = starting_score + (1 * tweet.favorite_count)
    baseScore = math.log(max(starting_score, 1))

    time_difference = (datetime.now() - tweet.created_at)
    time_difference_in_days = (time_difference.days * 86400 + time_difference.seconds) / 86400

    # start decaying the score after two days
    dropoff = 2
    if time_difference_in_days > dropoff:
        baseScore = baseScore * math.exp(-5 * (time_difference_in_days - dropoff) * (time_difference_in_days - dropoff))

    return baseScore


def _get_twitter_trends(client, woeid):
    response_data = client.trends_place(woeid)

    trends = []

    for content in (response_data[0]['trends']):
        trends.append(refine_hashtag(content['name']))

    return trends


@retry(wait_exponential_multiplier=1000, wait_exponential_max=20000)
def get_historical_trends(keywords):
    pytrends = get_pytrends()

    payload = {'q': keywords, 'date': 'now 1-H'}

    try:
        response = pytrends.trend(payload, return_type='json')
    except (ResponseError, JSONDecodeError, RateLimitError) as exception:
        raise Exception("Retry!")

    results = OrderedDict()

    for row in response['table']['rows']:
        results.update({row['c'][0]['f']: row['c'][1]['v']})

    print(str(results))

    return results


def get_zscore(keywords):
    historical_trends = []

    for date, value in get_historical_trends(keywords).items():
        historical_trends.append(value)

    historical_trends = list(reversed(historical_trends))

    historical_trends = [x for x in historical_trends if x is not None]

    current_trend = historical_trends[0]

    historical_trends = historical_trends[1:]

    zscore = ZScore(0.9, historical_trends)
    return zscore.score(current_trend)


# temp main method
if __name__ == "__main__":
    client = get_twitter_client()
    user = sys.argv[1]

    ##    feed = get_user_timeline_feed(client, user)
    ##    feed = get_bookmarks_feed(client, user)
    ##    feed = get_followings_feed(client, user)
    ##
    ##    for x in feed:
    ##        print(x.text + " " + str(x.score))

    lat = 7.2905720
    long = 80.6337260

    print(get_public_trends_feed(client, latitude=lat, longitude=long))
