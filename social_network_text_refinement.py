import re

from nltk.util import ngrams
from nltk import word_tokenize
from nltk.corpus import stopwords


def camel_case_split(text):
    matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', text)
    return [m.group(0) for m in matches]


def is_camel_case(text):
    return text != text.lower() and text != text.upper()


def is_english(s):
    try:
        s.encode('ascii')
    except UnicodeEncodeError:
        return False
    else:
        return True


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


def entity_frequency(entity, text):
    if not entity:
        return 0

    if not text:
        return 0

    stop_words = set(stopwords.words("english"))
    tokens = word_tokenize(entity)
    tokens = [word for word in tokens if word not in stop_words]

    sequences = []
    for number in range(1, len(tokens) + 1):
        n_grams = ngrams(tokens, number)

        for item in n_grams:
            word = ' '.join(item)
            frequency = text.count(word)

            if frequency > 0:
                sequences.append({'sequence': word, 'frequency': frequency})

    index = 0
    for item in sequences:
        if not (item['sequence'] == entity):
            count = item['frequency'] - text.count(entity)
            sequences[index]['frequency'] = count

        index += 1

    total = 0
    for sequence in sequences:
        total += sequence['frequency']

    return total


def entity_fraction_from_text(entities, text):
    if not entities:
        return []

    if not text:
        return []

    frequencies = []
    total_frequencies = 0
    for entity in entities:
        frequency = entity_frequency(entity, text)
        frequencies.append({'entity': entity, 'frequency': frequency})
        total_frequencies += frequency

    fractions = []
    for entry in frequencies:
        entity = entry['entity']

        fraction = entry['frequency']/total_frequencies
        fractions.append({'entity': entity, 'fraction': fraction})

    return fractions


if __name__ == "__main__":
    string = 'It is only two months since Henrikh Mkhitaryan was the man in the same position Anthony Martial ' \
             'currently finds himself in. Held accountable for a poor workrate in the derby defeat to Manchester City ' \
             'in September, Mkhitaryan had to take the long road back into Jose Mourinho’s plans. Mkhitaryan is ' \
             'a great player. Martial must learn from Mkhitaryan. Hail Henrikh Mkhitaryan. Come one Henrikh!!! ' \
             'European Organization for Nuclear Research is a great place to be. Anthony Martial has been to the ' \
             'Nuclear ' \
             'Research center. '

    term = 'Henrikh Mkhitaryan'

    # print(entity_frequency(term, string))
    # print()
    # print(entity_fraction_from_text(['Henrikh Mkhitaryan', 'Anthony Martial', 'Jose Mourinho'], string))

    # print(entity_fraction_from_text(['European Organization for Nuclear Research'], string))
    # print(entity_frequency('European Organization for Nuclear Research', string))
    # print(entity_frequency('Anthony Martial', string))
    # print(entity_frequency('Jayasuriya', string))
