# temp imports
import json
import os

from social_network_helper import get_named_entities, get_status_text, load_statuses


def compute_public_trends(trends):
    trend_text = ''
    for trend in trends:
        if trend is not None:
            trend_text += (trend + " ")

    print(trend_text)

    return get_named_entities(trend_text)


def compute_interests():
    ### temp implementation ###

    file_name = "statuses.jsonl"
    file_path = os.path.realpath('.') + '/' + file_name

    for keyyear, valueyear in load_statuses(file_path).items():
        print(keyyear)

        for month, monthval in valueyear.items():
            print(month)

            for val in monthval:
                print(val)

            print()

        print()

    ### temp implementation ###


    return None


def compute_community_interests():
    return None


def store_statuses(statuses):
    file_name = "statuses.jsonl"
    file_path = os.path.realpath('.') + '/' + file_name

    with open(file_path, 'a+') as file:
        for status in statuses:
            if status.text:
                file.write(json.dumps(get_status_text(status), default=jdefault) + "\n")


def jdefault(o):
    return o.__dict__


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

