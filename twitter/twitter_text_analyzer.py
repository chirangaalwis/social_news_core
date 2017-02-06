# -*- coding: utf-8 -*-
import os
import re
import sys

from nltk.tokenize import TweetTokenizer

sys.path.insert(0, os.path.realpath('..'))
from social_network_text_refinement import is_english, break_blocks


def refine_tweet_text(text):
    # removes re-tweet/via
    new_text = re.sub('[\s]*RT[\s]*|[\s]*via[\s]*', '', text)
    # new_text = re.sub('\s?RT.*:[\s]|\s?via.*:[\s]', '', text)

    # removes URLs
    new_text = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', new_text)

    # refine entities
    hashtag_pattern = re.compile('(\#\w+)')
    username_pattern = re.compile('(\@\w+)')

    for word in hashtag_pattern.findall(new_text):
        sub = refine_entities(word)
        if sub is not None:
            new_text = re.sub(word, sub, new_text)
        else:
            new_text = re.sub(word, '', new_text)

    for word in username_pattern.findall(new_text):
        sub = refine_entities(word)
        if sub is not None:
            new_text = re.sub(word, sub, new_text)
        else:
            new_text = re.sub(word, '', new_text)

    # remove starting and trailing whitespaces
    new_text = new_text.lstrip().rstrip()

    # tokenize the string and filter out non-English language usage
    tokenizer = TweetTokenizer()
    tokens = tokenizer.tokenize(new_text)
    new_text = " ".join([token for token in tokens if is_english(token)])

    return new_text


def refine_entities(entity):
    refined_entity = entity

    if refined_entity.startswith('#') | refined_entity.startswith('@'):
        refined_entity = refined_entity[1:]

    if not is_english(refined_entity):
        return None

    refined_entity = break_blocks(refined_entity)

    return refined_entity
