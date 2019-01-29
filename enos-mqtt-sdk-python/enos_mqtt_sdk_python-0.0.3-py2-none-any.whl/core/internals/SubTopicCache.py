

class SubTopicCache(object):

    def __init__(self):
        self.topicMap = dict()

    def exists(self, topic):
        return self.topicMap.has_key(topic)

    def put(self, topic):
        self.topicMap[topic] = ''

    def clean(self):
        self.topicMap.clear()