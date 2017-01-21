import re

def refine_tweet_text(text):
    # removes retweet/via
    new_text = re.sub('\s?RT.*:[\s]|\s?via.*:[\s]', '', text)
    new_text = re.sub('RT|via', '', new_text)
    # removes URLs
    new_text = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', new_text)
    return new_text

def refine_hashtag(hashtag):
    if hashtag.startswith('#'):
        hashtag = hashtag[1:]

##    indices = []
##    for m in re.finditer('[0-9]*', hashtag):
##        if m.match != '':
##            indices.append(m.start(0))
##            indices.append(m.end(0))

##    parts = [hashtag[i:j] for i,j in zip(indices, indices[1:]+[None])]
##
##    refined = ''
##    for part in parts:
##        refined += (part + " ")
##
##    refined = refined.strip()
    return re.finditer('[0-9]*', hashtag)
