import os, sys
from datetime import datetime
import math
import re

from twitter_client import TwitterClient
from twitter_text_analyzer import refine_tweet_text, refine_entities, is_english
sys.path.insert(0, os.path.realpath('..'))
from models import SocialNetworkFeed, SocialNetworkStatus


class TwitterFeedMapper(SocialNetworkFeed):
    CLIENT = TwitterClient()

    def get_public_trends_feed(self, **coordinates):
        # get world trends
        global_woeid = 1
        world_trends = self.get_twitter_trends(global_woeid)

        if ('latitude' in coordinates) & ('longitude' in coordinates):
            # get local trends
            response_data = self.CLIENT.client.trends_closest(coordinates['latitude'], coordinates['longitude'])
            locality_woeid = response_data[0]['woeid']
            local_trends = self.get_twitter_trends(locality_woeid)

            merged_trends = list(set(world_trends) | set(local_trends))
            return merged_trends
        else:
            return world_trends

    def get_user_timeline_feed(self):
        # capture the optional id value of the tweet since which tweets are to be returned
        last_id = None
        ids = self._load_latest_status_ids()
        if 'user_timeline' in ids:
            last_id = ids['user_timeline']

        # load tweets from user timeline
        if last_id is None:
            tweets = self.CLIENT.client.user_timeline(screen_name=self.CLIENT.username, count=10)
        else:
            tweets = self.CLIENT.client.user_timeline(screen_name=self.CLIENT.username, since_id=last_id)

        # convert tweets to application specific status objects
        statuses = self._convert_tweets_to_native_statuses(tweets)

        if len(statuses) > 0:
            self._update_latest_status_ids('user_timeline', statuses[0].id)

        return statuses

    def get_bookmarks_feed(self):
        # capture the optional id value of the tweet since which tweets are to be returned
        last_id = None
        ids = self._load_latest_status_ids()
        if 'bookmarks' in ids:
            last_id = ids['bookmarks']

        # load tweets from favorites
        if last_id is None:
            tweets = self.CLIENT.client.favorites(screen_name=self.CLIENT.username, count=10)
        else:
            tweets = self.CLIENT.client.favorites(screen_name=self.CLIENT.username, since_id=last_id)

        # convert tweets to application specific status objects
        statuses = self._convert_tweets_to_native_statuses(tweets)

        if len(statuses) > 0:
            self._update_latest_status_ids('bookmarks', statuses[0].id)

        return statuses

    def get_followings_feed(self):
        tweets = self.CLIENT.client.home_timeline(screen_name=self.CLIENT.username, count=5)

        # convert tweets to application specific status objects
        statuses = self._convert_tweets_to_native_statuses(tweets)

        return statuses

    def get_community_feed(self):
        lists = self.CLIENT.client.lists_all(screen_name=self.CLIENT.username)

        statuses = []
        for group in lists:
            statuses.extend(self.CLIENT.client.list_timeline(group.user.screen_name, group.slug, count=10))

        return self._convert_tweets_to_native_statuses(statuses)

    # support functions
    def _convert_tweets_to_native_statuses(self, tweets):
        statuses = []

        for tweet in tweets:
            statuses.append(SocialNetworkStatus(native_identifier=tweet.id, text=refine_tweet_text(tweet.text),
                                                created=str(tweet.created_at), score=self._generate_tweet_score(tweet)))

        return statuses

    @staticmethod
    def _load_latest_status_ids():
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

    def _update_latest_status_ids(self, key, value):
        file_name = "twitter_since_ids.txt"
        file_path = os.path.realpath('.') + '/' + file_name

        ids = self._load_latest_status_ids()

        ids[key] = value
        with open(file_path, 'w+') as file:
            for key, value in ids.items():
                file.write(key + ":" + str(value) + "\n")

    @staticmethod
    def _generate_tweet_score(tweet):
        starting_score = 100
        starting_score += 10 * tweet.retweet_count
        starting_score += 1 * tweet.favorite_count
        base_score = math.log(max(starting_score, 1))

        # time_difference = (datetime.now() - tweet.created_at)
        # time_difference_in_days = (time_difference.days * 86400 + time_difference.seconds) / 86400
        #
        # dropoff = 2
        # if time_difference_in_days > dropoff:
        #     base_score *= math.exp(
        #         -5 * (time_difference_in_days - dropoff) * (time_difference_in_days - dropoff))

        return base_score

    def get_twitter_trends(self, woeid):
        response_data = self.CLIENT.client.trends_place(woeid)

        trends = []

        for content in (response_data[0]['trends']):
            trends.append(refine_entities(content['name']))

        return trends


# temp main method
if __name__ == "__main__":
    # username = sys.argv[1]

    lat = 7.2905720
    long = 80.6337260

    mapper = TwitterFeedMapper()

    # print(mapper.get_public_trends_feed(latitude=lat, longitude=long))

    # mapper.get_followings_feed(username=username)

    # string = "Tonight we have @GordonRamsay, 高校からずっと一緒で本当に尊敬出来る先輩・布巻さんが今日ジョージア🇬🇪との試合で日本代表デビューします, @George_Osborne, @alessiacara and a demo from @ThisOldHouse! Happy #ThankYouNoteFriday! #FallonTonight"
    # string = '😂😱😂😱😂😱 https://t.co/XhYM6avCYO'
    # string = '高校からずっと一緒で本当に尊敬出来る先輩・布巻さんが今日ジョージア🇬🇪との試合で日本代表デビューします🇯🇵 活躍を祈ってます🔴⚪️ 皆さん応援よろしくお願いします👏 #東福岡 #早稲田 #Panasonic'
    # string = 'केंद्रीय वित्त मंत्री @arunjaitley ने #Budget2017 के बाद उद्योग संगठनों से की चर्चा'

    # print(string)
    #
    # hashtag_pattern = re._compile('(\#\w+)', flags=0)
    # username_pattern = re._compile('(\@\w+)', flags=0)
    #
    # for word in hashtag_pattern.findall(string):
    #     string = re.sub(word, refine_entities(word), string)
    #
    # for word in username_pattern.findall(string):
    #     string = re.sub(word, refine_entities(word), string)
    #
    # print(string)

    list = mapper.get_community_feed()

    for item in list:
        print(item.text + ": " + str(item.score))
