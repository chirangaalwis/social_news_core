import re


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
