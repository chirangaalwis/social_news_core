class SocialNetworkStatus:
    
    def __init__(self, text, score, native_identifier = None, created = None):
        self.id = native_identifier
        self.text = text
        self.created = created
        self.score = score

class Tag:

    def __init__(self, topic, context):
        self.topic = topic
        self.context = context

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            topic_equals = (self.text == other.text)
            context_equals = (set(self.context) == set(other.context))

            return topic_equals & context_equals
        else:
            return false

    def __ne__(self, other):
        return not self.__eq__(other)



