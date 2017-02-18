import math
import os
import sys
import re

sys.path.insert(0, os.path.realpath('..'))
from models import SocialNetworkStatus, SocialNetworkMember
from twitter_text_analyzer import refine_tweet_text


def convert_tweets_to_native_statuses(tweets):
    statuses = []

    for tweet in tweets:
        statuses.append(SocialNetworkStatus(native_identifier=tweet.id,
                                            text=refine_tweet_text(tweet.text), created=str(tweet.created_at),
                                            score=_generate_tweet_score(tweet.retweet_count, tweet.favorite_count)))

    return statuses


def get_member_instance(member_identifier, content):
    if not member_identifier:
        return None

    return SocialNetworkMember(identifier=member_identifier, content=content)


def load_latest_status_ids():
    file_name = "twitter_since_ids.txt"
    file_path = os.path.realpath('.') + '/' + file_name

    ids = dict()

    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            for line in file:
                if ":" in line:
                    content = re.split('[:]', line)
                    ids[content[0]] = content[1].strip('\n')

    return ids


def update_latest_status_ids(key, value):
    file_name = "twitter_since_ids.txt"
    file_path = os.path.realpath('.') + '/' + file_name

    ids = load_latest_status_ids()

    ids[key] = value
    with open(file_path, 'w+') as file:
        for key, value in ids.items():
            file.write(key + ":" + str(value) + "\n")


def _generate_tweet_score(share_count, favorite_count):
    starting_score = 100
    starting_score += 10 * share_count
    starting_score += 1 * favorite_count
    base_score = math.log(max(starting_score, 1))

    return base_score
