import os
import sys
from tweepy import API
from tweepy import OAuthHandler


class TwitterClient:
    def __init__(self):
        self.client = self.get_twitter_client()
        self.username = self.get_twitter_username()

    def get_twitter_client(self):
        authentication = self.get_twitter_auth()
        client = API(authentication)
        return client

    @staticmethod
    def get_twitter_username():
        try:
            username = os.environ['TWITTER_USERNAME']
        except KeyError:
            sys.stderr.write("TWITTER_USERNAME environment variable not set\n")
            sys.exit(1)

        return username

    @staticmethod
    def get_twitter_auth():
        try:
            consumer_key = os.environ['TWITTER_CONSUMER_KEY']
            consumer_secret = os.environ['TWITTER_CONSUMER_SECRET']
            access_token = os.environ['TWITTER_ACCESS_TOKEN']
            access_secret = os.environ['TWITTER_ACCESS_SECRET']
        except KeyError:
            sys.stderr.write("TWITTER_* environment variables not set\n")
            sys.exit(1)

        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_secret)
        return auth

if __name__ == "__main__":
    client = TwitterClient()

    lists = client.client.lists_all()

    statuses = []

    for list in lists:
        statuses.extend(client.client.list_timeline(list.user.screen_name, list.slug, count=10))

    for status in statuses:
        print(status.text)
        print()
        # for obj in status:
        #     print(obj)
        #     print()

    # for list in lists:
    #     print(list.full_name)
    #     print()
