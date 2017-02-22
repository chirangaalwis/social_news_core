import os
import sys

from models import SocialNetworkFeed
from social_network_helper import store_statuses

sys.path.insert(0, os.path.realpath('twitter/'))
from twitter_feed_mapper import TwitterFeedMapper

SOCIAL_NETWORK_FEED = [TwitterFeedMapper()]
STATUSES_FILE_PATH = os.path.realpath('.') + '/statuses.jsonl'
BOOKMARKS_FILE_PATH = os.path.realpath('.') + '/bookmarks.jsonl'


# TODO: TEMP CO-ORDINATES
LATITUDE = 7.2905720
LONGITUDE = 80.6337260


def load_trends():
    trends = []

    for feed in SOCIAL_NETWORK_FEED:
        if isinstance(feed, SocialNetworkFeed):
            trends.extend(feed.get_public_trends_feed(latitude=LATITUDE, longitude=LONGITUDE))

    return trends


def load_user_timeline_feed():
    statuses = []

    for feed in SOCIAL_NETWORK_FEED:
        if isinstance(feed, SocialNetworkFeed):
            statuses.extend(feed.get_user_timeline_feed())

    return statuses


def load_bookmarks_feed():
    statuses = []

    for feed in SOCIAL_NETWORK_FEED:
        if isinstance(feed, SocialNetworkFeed):
            statuses.extend(feed.get_bookmarks_feed())

    return statuses


def load_followings_feed():
    statuses = []

    for feed in SOCIAL_NETWORK_FEED:
        if isinstance(feed, SocialNetworkFeed):
            statuses.extend(feed.get_followings_feed())

    return statuses


def load_community_feed():
    members = []

    for feed in SOCIAL_NETWORK_FEED:
        if isinstance(feed, SocialNetworkFeed):
            members.extend(feed.get_community_feed())

    return members


def store_user_timeline_feed(statuses):
    if statuses:
        store_statuses(statuses, STATUSES_FILE_PATH)


def store_bookmarks_feed(statuses):
    if statuses:
        store_statuses(statuses, BOOKMARKS_FILE_PATH)
