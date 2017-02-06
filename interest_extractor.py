from social_network_helper import get_named_entities
from social_network_data_updater import load_user_timeline_feed, load_bookmarks_feed, load_followings_feed, store_user_timeline_feed, store_bookmarks_feed


def compute_public_trends(trends):
    trend_text = ''
    for trend in trends:
        if trend is not None:
            trend_text += (trend + " ")

    print(trend_text)

    return get_named_entities(trend_text)


def compute_interests():
    ### temp implementation ###

    store_user_timeline_feed(load_user_timeline_feed())
    store_bookmarks_feed(load_bookmarks_feed())

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

    compute_interests()

