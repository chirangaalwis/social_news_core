# -*- coding: utf-8 -*-
import re

def refine_tweet_text(text):
    # removes retweet/via
    new_text = re.sub('\s?RT.*:[\s]|\s?via.*:[\s]', '', text)
    new_text = re.sub('RT|via', '', new_text)
    # removes URLs
    new_text = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', new_text)
    return new_text

def refine_hashtag(hashtag):

    refined_hashtag = hashtag
    
    if refined_hashtag.startswith('#'):
        refined_hashtag = refined_hashtag[1:]

    if not _isEnglish(refined_hashtag):
        return None

    refined_hashtag = _break_number_blocks(refined_hashtag)
    
    return refined_hashtag

def _isEnglish(s):
    try:
        s.encode('ascii')
    except UnicodeEncodeError:
        return False
    else:
        return True

def _camel_case_split(text):
    
    matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', text)
    return [m.group(0) for m in matches]

def _is_camel_case(text):
    
    return (text != text.lower() and text != text.upper())

def _break_number_blocks(text):

    pattern = re.compile("([\d+])")
    original = pattern.split(text)
    original = list(filter(None, original))
##    print(original)
    
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
            
            if _is_camel_case(non_digit):
                non_digit = _camel_case_split(non_digit)
                words.extend(non_digit)
            else:
                words.append(non_digit)
            
            index += 1

##        print(str(words))

    return " ".join(words)

# temp main method
if __name__ == "__main__":

##    s = "MUFC1958April68 BusbyBabes njfnlk "

##    print(_break_number_blocks(s))

    s = "01ManchesterUnitedFC1958AprilTheFlowersOfManchester4Ever"
##    s = "umk17"
    s = _break_number_blocks(s)
    print(s)
