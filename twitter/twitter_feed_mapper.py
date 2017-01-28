import os, sys
from datetime import datetime
import math
import re

import json

from twitter_client import get_twitter_client
from twitter_text_analyzer import refine_tweet_text, refine_hashtag
sys.path.insert(0, os.path.realpath('..'))
from models import SocialNetworkStatus

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

    if(('latitude' in coordinates) & ('longitude' in coordinates)):
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
        statuses.append(SocialNetworkStatus(native_identifier = tweet.id, text = refine_tweet_text(tweet.text), created = str(tweet.created_at), score = _generate_score(tweet)))

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

    ids[key] =  value
    with open(file_path, 'w+') as file:
        for key, value in ids.items():
            file.write(key + ":" + str(value) +"\n")

def _generate_score(tweet):

    starting_score = 100
    starting_score = starting_score + (10*tweet.retweet_count)
    starting_score = starting_score + (1*tweet.favorite_count)
    baseScore = math.log(max(starting_score,1))

    time_difference = (datetime.now() - tweet.created_at)
    time_difference_in_days = (time_difference.days * 86400 + time_difference.seconds)/86400

    # start decaying the score after two days
    dropoff = 2
    if time_difference_in_days > dropoff:
        baseScore = baseScore * math.exp(-5 * (time_difference_in_days - dropoff) * (time_difference_in_days - dropoff))

    return baseScore

def _get_twitter_trends(client, woeid):
    
    response_data = client.trends_place(woeid)

    trends = []

    for content in (response_data[0]['trends']):
        print(content['name'])
        trends.append(refine_hashtag(content['name']))

    return trends

##def _store_tweets(statuses, file_path):
##    with open(file_path, 'a+') as file:
##        for status in reversed(statuses):
##            file.write(json.dumps(status, default=jdefault)+"\n")
##
##def _load_tweets(file_path):
##    data = []
##    if os.path.exists(file_path):
##        with open(file_path, 'r') as file:
##            for line in file:
##                status = json.loads(line)
##                data.append(SocialNetworkStatus(native_identifier = status['id'], text = status['text'], created = datetime.strptime(status['created'],'%Y-%m-%d %H:%M:%S'), score = status['score']))
##
##    return data
##
##def jdefault(o):
##    return o.__dict__

##def _generate_score(tweet):
##    retweet_score = math.sqrt(1 + 10*tweet.retweet_count)/(1 + 10*tweet.retweet_count)
##
##    time_difference = (datetime.now() - tweet.created_at)
##    time_difference_in_mins = divmod(time_difference.days * 86400 + time_difference.seconds, 60)
##
##    print(tweet.text)
##    print(tweet.created_at)
##    print('o' + str(time_difference_in_mins))
##    
##    if time_difference_in_mins[1] > 30:
##        time_difference_in_mins = time_difference_in_mins[0] + 1
##    else:
##        time_difference_in_mins = time_difference_in_mins[0]
##
##    print('min' + str(time_difference_in_mins))
##    print('likes ' + str(tweet.favorite_count))
##    score = (math.sqrt(1 + tweet.favorite_count)/(1 + tweet.favorite_count)) + ((2*math.log(1 + tweet.favorite_count))/(1 + math.log(1 + (0.85*time_difference_in_mins))))
##    score = ((2*math.log(1 + tweet.favorite_count))/(1 + math.log(1 + (0.85*time_difference_in_mins))))


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
