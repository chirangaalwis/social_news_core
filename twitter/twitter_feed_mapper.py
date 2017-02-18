import os
import sys
from tweepy.error import TweepError

from twitter_client import TwitterClient
from twitter_helper import convert_tweets_to_native_statuses, load_latest_status_ids, update_latest_status_ids,\
    get_member_instance
from twitter_text_analyzer import refine_entities, refine_tweet_text
sys.path.insert(0, os.path.realpath('..'))
from models import SocialNetworkFeed


class TwitterFeedMapper(SocialNetworkFeed):
    CLIENT = TwitterClient()

    def get_public_trends_feed(self, **coordinates):
        # get world trends
        global_woe_id = 1
        world_trends = self.get_twitter_trends(global_woe_id)

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
        ids = load_latest_status_ids()
        if 'user_timeline' in ids:
            last_id = ids['user_timeline']

        # load tweets from user timeline
        if last_id is None:
            tweets = self.CLIENT.client.user_timeline(screen_name=self.CLIENT.username, count=10)
        else:
            tweets = self.CLIENT.client.user_timeline(screen_name=self.CLIENT.username, since_id=last_id)

        # convert tweets to application specific status objects
        statuses = convert_tweets_to_native_statuses(tweets)

        if len(statuses) > 0:
            update_latest_status_ids('user_timeline', statuses[0].id)

        return statuses

    def get_bookmarks_feed(self):
        # capture the optional id value of the tweet since which tweets are to be returned
        last_id = None
        ids = load_latest_status_ids()
        if 'bookmarks' in ids:
            last_id = ids['bookmarks']

        # load tweets from favorites
        if last_id is None:
            tweets = self.CLIENT.client.favorites(screen_name=self.CLIENT.username, count=10)
        else:
            tweets = self.CLIENT.client.favorites(screen_name=self.CLIENT.username, since_id=last_id)

        # convert tweets to application specific status objects
        statuses = convert_tweets_to_native_statuses(tweets)

        if len(statuses) > 0:
            update_latest_status_ids('bookmarks', statuses[0].id)

        return statuses

    def get_followings_feed(self):
        tweets = self.CLIENT.client.home_timeline(screen_name=self.CLIENT.username, count=5)

        # convert tweets to application specific status objects
        statuses = convert_tweets_to_native_statuses(tweets)

        return statuses

    def get_community_feed(self):
        lists = self.CLIENT.client.lists_all(screen_name=self.CLIENT.username)

        members = []
        for community in lists:
            members.extend(self.get_list_member_content(community.user.screen_name, community.slug))

        return members

    # support functions
    def get_twitter_trends(self, woe_id):
        response_data = self.CLIENT.client.trends_place(woe_id)

        trends = []

        for content in (response_data[0]['trends']):
            trends.append(refine_entities(content['name']))

        return trends

    def get_statuses_text(self, username):
        if username:
            try:
                tweets = self.CLIENT.client.user_timeline(screen_name=username, count=5)
            except TweepError:
                return None

            content = []
            for tweet in tweets:
                content.append(refine_tweet_text(tweet.text))

            return " ".join(content)
        else:
            return None

    def get_list_member_content(self, owner, slug):
        if owner and slug:
            members = self.CLIENT.client.list_members(owner, slug)

            member_screen_names = [member.screen_name for member in members]

            member_content = []
            for identifier in member_screen_names:
                member_content.append(get_member_instance(identifier, self.get_statuses_text(identifier)))

            print(member_content)
            return member_content
        else:
            return None


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

    print(mapper.get_community_feed())
