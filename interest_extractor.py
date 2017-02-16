from social_network_helper import get_named_entities, load_statuses, get_zscore
from social_network_data_updater import load_user_timeline_feed, load_bookmarks_feed, load_followings_feed, \
    store_user_timeline_feed, store_bookmarks_feed, load_trends

from models import SocialNetworkTrend

import os

STATUSES_FILE_PATH = os.path.realpath('.') + '/statuses.jsonl'
BOOKMARKS_FILE_PATH = os.path.realpath('.') + '/bookmarks.jsonl'


def compute_public_trends():
    trend_text = ''
    for trend in load_trends():
        if trend is not None:
            trend_text += (trend + " ")

    tags = set(get_named_entities(trend_text))

    trends = []

    for tag in tags:
        topic = tag.topic
        z_score = get_zscore(topic)
        trends.append(SocialNetworkTrend(tag, z_score))

    for trend in trends:
        print(trend.tags.topic)
        print(str(trend.score))
        print()


def compute_interests():
    ### temp implementation ###

    # store_user_timeline_feed(load_user_timeline_feed())
    # store_bookmarks_feed(load_bookmarks_feed())


    dictionary = load_statuses(STATUSES_FILE_PATH)

    for year, months in dictionary.items():

        print('Year: ' + str(year))

        for month, statuses in months.items():

            print('Month: ' + str(month))

            for status in statuses:
                if len(status['Tags']) == 0:
                    continue

                print('Status score: ' + str(status['Score']))
                for tag in status['Tags']:
                    print('Entity: ' + tag['topic'])
                    print('Score: ' + str(tag['context_fraction'] * status['Score']))
                    print('Type: ' + tag['context']['type'])
                    print('Description: ' + tag['context']['description'])
                    print()
                print()

            print()

        print()


    ### temp implementation ###


    return None


def compute_community_interests():
    return None


# temp main method
if __name__ == "__main__":
    # username = sys.argv[1]

    # lat = 7.2905720
    # long = 80.6337260
    #
    # tags = compute_public_trends(get_public_trends_feed(client, latitude=lat, longitude=long))
    #
    # for tag in tags:
    #     print(tag.topic + " " + str(tag.context))

    # compute_interests()

    compute_public_trends()
