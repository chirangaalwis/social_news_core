from math import sqrt


class SocialNetworkFeed:
    def get_public_trends_feed(self, **coordinates):
        pass

    def get_user_timeline_feed(self):
        pass

    def get_bookmarks_feed(self):
        pass

    def get_followings_feed(self):
        pass

    def get_community_feed(self):
        pass


class SocialNetworkStatus:
    def __init__(self, text, score, native_identifier=None, created=None):
        self.id = native_identifier
        self.text = text
        self.created = created
        self.score = score

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            text_equals = (self.text == other.text)

            return text_equals
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


class SocialNetworkTrend:
    def __init__(self, tags, score):
        self.tags = tags
        self.score = score

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            for tag in self.tags:
                exists = any(other_tag == tag for other_tag in other.tags)
                if not exists:
                    return False

            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


class Tag:
    def __init__(self, topic, context):
        self.topic = topic
        self.context = context

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            topic_equals = (self.topic.lower() == other.topic.lower())
            type_equals = (self.context['type'] == other.context['type'])
            sub_type_equals = (set(self.context['sub_types']) == set(other.context['sub_types']))

            return topic_equals & type_equals & sub_type_equals
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        product_of_context = 1
        for character in self.topic:
            product_of_context *= ord(character)

        for character in self.context['type']:
            product_of_context *= ord(character)

        for value in self.context['sub_types']:
            for character in value:
                product_of_context *= ord(character)

        return product_of_context


class ZScore:
    def __init__(self, decay, past=None):
        if past is None:
            past = []
        self.sqrAvg = self.avg = 0

        # The rate at which the historic data's effect will diminish.
        self.decay = decay

        for x in past: self.update(x)

    def update(self, value):
        # Set initial averages to the first value in the sequence.
        if self.avg == 0 and self.sqrAvg == 0:
            self.avg = float(value)
            self.sqrAvg = float((value ** 2))
        # Calculate the average of the rest of the values using a
        # floating average.
        else:
            self.avg = self.avg * self.decay + value * (1 - self.decay)
            self.sqrAvg = self.sqrAvg * self.decay + (value ** 2) * (1 - self.decay)
        return self

    def std(self):
        # Somewhat ad-hoc standard deviation calculation.
        return sqrt(self.sqrAvg - self.avg ** 2)

    def score(self, obs):
        if self.std() == 0:
            return (obs - self.avg) * float("infinity")
        else:
            return (obs - self.avg) / self.std()
