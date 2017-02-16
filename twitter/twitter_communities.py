from twitter_client import TwitterClient
from twitter_text_analyzer import refine_tweet_text, refine_entities, is_english
from tweepy.error import TweepError

import sys
import json
from argparse import ArgumentParser
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

CLIENT = TwitterClient()


def get_statuses_text(username):
    if username:
        try:
            tweets = CLIENT.client.user_timeline(screen_name=username, count=10)
        except TweepError:
            return None

        content = []
        for tweet in tweets:
            content.append(refine_tweet_text(tweet.text))

        return " ".join(content)
    else:
        return None


def get_list_member_content(owner, slug):
    if owner and slug:
        members = CLIENT.client.list_members(owner, slug)

        member_screen_names = [member.screen_name for member in members]

        member_content = {}
        for identifier in member_screen_names:
            member_content[identifier] = get_statuses_text(identifier)

        return member_content
    else:
        return None


def get_parser():
    parser = ArgumentParser("Clustering of followers")

    parser.add_argument('--filename')
    parser.add_argument('--k', type=int)
    parser.add_argument('--min-df', type=int, default=2)
    parser.add_argument('--max-df', type=float, default=0.8)
    parser.add_argument('--max-features', type=int, default=None)
    parser.add_argument('--no-idf', dest='use_idf', default=True,
                        action='store_false')
    parser.add_argument('--min-ngram', type=int, default=1)
    parser.add_argument('--max-ngram', type=int, default=1)
    return parser


# temp main method
if __name__ == "__main__":
    # lists = CLIENT.client.lists_all(screen_name=CLIENT.username)
    #
    # statuses = []
    # for group in lists:
    #     print(group.user.screen_name + ' ' + group.slug)

    # statuses.extend(CLIENT.client.list_timeline(group.user.screen_name, group.slug, count=10))
    # print(get_list_member_content(group.user.screen_name, group.slug))

    # print(get_list_member_content('chirangaalwis', 'manchesteruniteddiehard'))



    # parser = get_parser()
    # args = parser.parse_args()
    # if args.min_ngram > args.max_ngram:
    #     print("Error: incorrect value for --min-ngram ({}): it can't be higher than - -max - value({}) ".format(args.min_ngram, args.max_ngram))
    #     sys.exit(1)
    # with open(args.filename) as f:
    #     users = []
    #     for line in f:
    #         profile = json.loads(line)
    #         users.append(profile['description'])
    #     # create vectorizer
    #     vectorizer = TfidfVectorizer(max_df=args.max_df, min_df = args.min_df, max_features = args.max_features, stop_words = 'english', ngram_range = (args.min_ngram, args.max_ngram), use_idf = args.use_idf)

    users = []
    for k, v in get_list_member_content('bd_wheeler', 'sf-devops-influencers').items():
        users.append(v)

    vectorizer = TfidfVectorizer(max_df=0.8, min_df=2, max_features=200,
                                 stop_words='english', ngram_range=(1, 3),
                                 use_idf=True)
    # fit data
    X = vectorizer.fit_transform(users)
    print("Data dimensions: {}".format(X.shape))
    # perform clustering
    km = KMeans(n_clusters=int(len(users)/2))
    km.fit(X)
    clusters = defaultdict(list)
    for i, label in enumerate(km.labels_):
        clusters[label].append(users[i])
    # print 10 user description for this cluster
    for label, descriptions in clusters.items():
        print('---------- Cluster {}'.format(label + 1))
    for desc in descriptions[:20]:
        print(desc)
