import os, sys, json
from datetime import datetime
import datetime as dt

from twitter_client import get_twitter_client
from twitter_text_analyzer import refine_tweet_text
sys.path.insert(0, os.path.realpath('..'))
from models import SocialNetworkStatus

def get_user_timeline_feed(client, username):
    file_name = "user_timeline_{}.jsonl".format(username)
    file_path = os.path.realpath('.') + '/tweets/' + file_name

    # load existing, stored tweets
    existing = _load_tweets(file_path)

    # load tweets from user timeline
    if len(existing) > 0:
        latest_status = existing[-1]
        tweets = client.user_timeline(screen_name=username, since_id=latest_status.id)
    else:
        tweets = client.user_timeline(screen_name=username, count=30)

    # convert tweets to application specific status objects
    statuses = _convert_tweets_to_native_statuses(tweets)
    
    # store the collected tweets for future processing
    _store_tweets(statuses, file_path)

    # load existing, stored tweets (after storing the latest)
    current = _load_tweets(file_path)

    # load and return all texts of tweets made during the last 7 days
    one_week_back = datetime.now() - dt.timedelta(days=7)
    feed = []
    for current_status in current:
        if current_status.created > one_week_back:
            feed.append(current_status)

    return feed

def get_bookmarks_feed(client, username):
    file_name = "favorites_{}.jsonl".format(username)
    file_path = os.path.realpath('.') + '/tweets/' + file_name

    # load existing, stored tweets
    existing = _load_tweets(file_path)

    # load favorite tweets
    if len(existing) > 0:
        latest_status = existing[-1]
        tweets = client.favorites(screen_name=username, since_id=latest_status.id)
    else:
        tweets = client.favorites(screen_name=username, count=30)

    # convert tweets to application specific status objects
    statuses = _convert_tweets_to_native_statuses(tweets)
    
    # store the collected tweets for future processing
    _store_tweets(statuses, file_path)

    # load existing, stored tweets (after storing the latest)
    current = _load_tweets(file_path)

    # load and return all texts of tweets made during the last 7 days
    one_week_back = datetime.now() - dt.timedelta(days=7)
    feed = []
    for current_status in current:
        if current_status.created > one_week_back:
            feed.append(current_status)

    return feed

def get_followings_feed(client, username):
    file_name = "home_timeline_{}.jsonl".format(username)
    file_path = os.path.realpath('.') + '/tweets/' + file_name

    tweets = client.home_timeline(screen_name=username, count=50)
    statuses = _convert_tweets_to_native_statuses(tweets)
    _store_tweets(statuses, file_path)

    return statuses

# helper functions
def _convert_tweets_to_native_statuses(tweets):
    statuses = []

    for tweet in tweets:
        statuses.append(SocialNetworkStatus(native_identifier = tweet.id, text = refine_tweet_text(tweet.text), created = str(tweet.created_at), score = 0))

    return statuses

def _store_tweets(statuses, file_path):
    with open(file_path, 'a+') as file:
        for status in reversed(statuses):
            file.write(json.dumps(status, default=jdefault)+"\n")

def _load_tweets(file_path):
    data = []
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            for line in file:
                status = json.loads(line)
                data.append(SocialNetworkStatus(native_identifier = status['id'], text = status['text'], created = datetime.strptime(status['created'],'%Y-%m-%d %H:%M:%S'), score = status['score']))

    return data

def jdefault(o):
    return o.__dict__


# temp main method
if __name__ == "__main__":
    client = get_twitter_client()

    user = sys.argv[1]
##    feed = get_user_timeline_feed(client, user)
##    feed = get_bookmarks_feed(client, user)
##    feed = get_followings_feed(client, user)

##    for x in feed:
##        print(x.text + " " + str(x.score))

    
