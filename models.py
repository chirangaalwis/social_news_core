class SocialNetworkStatus:
    
    def __init__(self, text, score, native_identifier = None, created = None):
        self.id = native_identifier
        self.text = text
        self.created = created
        self.score = score
