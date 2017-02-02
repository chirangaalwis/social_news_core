from models import SocialNetworkStatus, Tag

# temp imports
import os, sys
sys.path.insert(0, os.path.realpath('twitter/'))
from twitter_feed_mapper import get_user_timeline_feed, get_bookmarks_feed, get_followings_feed, get_public_trends_feed
from twitter_client import get_twitter_client
# temp to remove unsupported languages
##from string import ascii_letters


import json

from alchemyapi import AlchemyAPI

def compute_public_trends(trends):

    trend_text = ''
    for trend in trends:
        if trend is not None:
            
            trend_text += (trend + " ")

    print(trend_text)
    
    return get_named_entities(trend_text)

def compute_interests():
    ### temp implementation ###

    for status in load_statuses():
        print(status['Tags'])
        print(status['Score'])

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
                file.write(json.dumps(get_tags_per_status(status), default=jdefault)+"\n")

def jdefault(o):
    return o.__dict__

def load_statuses():

    file_name = "statuses.jsonl"
    file_path = os.path.realpath('.') + '/' + file_name
    
    data = []

    with open(file_path, 'r') as file:
        for line in file:
            status = json.loads(line)
            data.append(status)

    return data

def get_tags_per_status(status):

    status_record = {'Id': status.id, 'Created_At': status.created, 'Score': status.score, 'Tags': get_named_entities(status.text)}

    return status_record

def get_named_entities(text):
    
    tags = []

    # Create the AlchemyAPI Object
    alchemyapi = AlchemyAPI()

    response = alchemyapi.entities('text', text)

    if response['status'] == 'OK':
        for entity in response['entities']:
            tags.append(Tag(entity['text'], [entity['type']]))
    else:
        print('Error in entity extraction call: ', response['statusInfo'])

    return tags

# temp main method
if __name__ == "__main__":

    username = sys.argv[1]
    client = get_twitter_client()
##    statuses = get_user_timeline_feed(client, username) + get_bookmarks_feed(client, username) + get_followings_feed(client, username)

##    statuses = get_user_timeline_feed(client, username)
##
##    store_statuses(statuses)
##
##    compute_interests()
    
    lat = 7.2905720
    long = 80.6337260

    tags = compute_public_trends(get_public_trends_feed(client, latitude=lat, longitude=long))

    for tag in tags:
        print(tag.topic + " " + str(tag.context))
    
