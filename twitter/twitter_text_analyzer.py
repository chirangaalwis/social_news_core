# -*- coding: utf-8 -*-
import re
from nltk.tokenize import TweetTokenizer


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


def is_english(s):
    try:
        s.encode('ascii')
    except UnicodeEncodeError:
        return False
    else:
        return True


def camel_case_split(text):
    matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', text)
    return [m.group(0) for m in matches]


def is_camel_case(text):
    return text != text.lower() and text != text.upper()


def break_blocks(text):
    pattern = re.compile("([\d+])")
    original = pattern.split(text)
    original = list(filter(None, original))

    words = []

    index = 0
    while index < len(original):

        if pattern.match(original[index]):

            word = str(original[index])
            for inner_index in range(index + 1, len(original)):

                if pattern.match(original[inner_index]):
                    word += str(original[inner_index])
                    index += 1
                else:
                    break

            words.append(word.strip())
            index += 1

        else:

            non_digit = (original[index]).strip()

            if '_' in non_digit:
                split = non_digit.split('_')
                words.extend(split)
            elif is_camel_case(non_digit):
                non_digit = camel_case_split(non_digit)
                words.extend(non_digit)
            else:
                words.append(non_digit)

            index += 1

    return " ".join(words)


# temp main method
if __name__ == "__main__":
    ##    s = "MUFC1958April68 BusbyBabes njfnlk "

    ##    print(_break_number_blocks(s))

    # hashtag = "01ManchesterUnitedFC1958AprilTheFlowersOfManchester4Ever"
    # hashtag = _break_number_blocks(hashtag)
    # print(hashtag)

    # string = 'NZvsAUS'
    # string = 'WOMENForTRUMP'
    # print(camel_case_split(string))

    print(break_blocks('1234PythonLanguage3.5.2SomeText'))


