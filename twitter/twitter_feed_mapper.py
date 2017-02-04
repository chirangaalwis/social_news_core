#!/usr/bin/python3

import os, sys
from datetime import datetime
import math
import re
from json import JSONDecodeError
from pytrends.request import ResponseError, RateLimitError
from retrying import retry

from collections import OrderedDict

from twitter_client import TwitterClient
from twitter_text_analyzer import refine_tweet_text, refine_entities, is_english

sys.path.insert(0, os.path.realpath('..'))
from google_trends_client import get_pytrends
from models import SocialNetworkStatus, ZScore


class TwitterFeedMapper:

    GOOGLE_TRENDS = get_pytrends()
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

    @retry(wait_exponential_multiplier=1000, wait_exponential_max=20000)
    def get_historical_trends(self, keywords):
        payload = {'q': keywords, 'date': 'now 1-H'}

        try:
            response = self.GOOGLE_TRENDS.trend(payload, return_type='json')
        except (ResponseError, JSONDecodeError, RateLimitError) as exception:
            raise Exception("Retry!")

        results = OrderedDict()

        for row in response['table']['rows']:
            results.update({row['c'][0]['f']: row['c'][1]['v']})

        print(str(results))

        return results

    def get_zscore(self, keywords):
        historical_trends = []

        for date, value in self.get_historical_trends(keywords).items():
            historical_trends.append(value)

        historical_trends = list(reversed(historical_trends))

        historical_trends = [x for x in historical_trends if x is not None]

        current_trend = historical_trends[0]

        historical_trends = historical_trends[1:]

        z_score = ZScore(0.9, historical_trends)
        return z_score.score(current_trend)



    def get_user_timeline_feed(self, username):
        # capture the optional id value of the tweet since which tweets are to be returned
        last_id = None
        ids = self._load_latest_status_ids()
        if 'user_timeline' in ids:
            last_id = ids['user_timeline']

        # load tweets from user timeline
        if last_id is None:
            tweets = self.CLIENT.client.user_timeline(screen_name=username, count=30)
        else:
            tweets = self.CLIENT.client.user_timeline(screen_name=username, since_id=last_id)

        # convert tweets to application specific status objects
        statuses = self._convert_tweets_to_native_statuses(tweets)

        if len(statuses) > 0:
            self._update_latest_status_ids('user_timeline', statuses[0].id)

        return statuses

    def get_bookmarks_feed(self, username, **optional):
        # capture the optional id value of the tweet since which tweets are to be returned
        last_id = None
        ids = self._load_latest_status_ids()
        if ('bookmarks' in ids):
            last_id = ids['bookmarks']

        # load tweets from favorites
        if last_id is None:
            tweets = self.CLIENT.client.favorites(screen_name=username, count=30)
        else:
            tweets = self.CLIENT.client.favorites(screen_name=username, since_id=last_id)

        # convert tweets to application specific status objects
        statuses = self._convert_tweets_to_native_statuses(tweets)

        if len(statuses) > 0:
            self._update_latest_status_ids('bookmarks', statuses[0].id)

        return statuses

    def get_followings_feed(self, username):
        tweets = self.CLIENT.client.home_timeline(screen_name=username, count=50)

        # convert tweets to application specific status objects
        statuses = self._convert_tweets_to_native_statuses(tweets)

        return statuses

    # support functions
    def _convert_tweets_to_native_statuses(self, tweets):
        statuses = []

        for tweet in tweets:
            print(tweet.text)

            print(refine_tweet_text(tweet.text))

            print()

        # for tweet in tweets:
        #     statuses.append(SocialNetworkStatus(native_identifier=tweet.id, text=refine_tweet_text(tweet.text),
        #                                         created=str(tweet.created_at), score=self._generate_tweet_score(tweet)))

        return statuses

    @staticmethod
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

    def _update_latest_status_ids(self, key, value):
        file_name = "since_ids.txt"
        file_path = os.path.realpath('.') + '/' + file_name

        ids = self._load_latest_status_ids()

        ids[key] = value
        with open(file_path, 'w+') as file:
            for key, value in ids.items():
                file.write(key + ":" + str(value) + "\n")

    def _generate_tweet_score(self, tweet):
        starting_score = 100
        starting_score = starting_score + (10 * tweet.retweet_count)
        starting_score = starting_score + (1 * tweet.favorite_count)
        baseScore = math.log(max(starting_score, 1))

        time_difference = (datetime.now() - tweet.created_at)
        time_difference_in_days = (time_difference.days * 86400 + time_difference.seconds) / 86400

        # start decaying the score after two days
        dropoff = 2
        if time_difference_in_days > dropoff:
            baseScore = baseScore * math.exp(
                -5 * (time_difference_in_days - dropoff) * (time_difference_in_days - dropoff))

        return baseScore

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

