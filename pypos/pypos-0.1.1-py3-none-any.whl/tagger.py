import re
import pickle
import numpy as np
from pypos.hmm import HMM

TAGNAMES = {
    'CC': 'Coordinating conjunction', 'CD': 'Cardinal number', 'DT': 'Determiner', 'EX': 'Existential there', 'FW': 'Foreign word', 'IN': 'Preposition or subordinating conjunction', 'JJ': 'Adjective', 'JJR': 'Adjective, comparative',
    'JJS': 'Adjective, superlative', 'LS': 'List item marker', 'MD': 'Modal', 'NN': 'Noun, singular or mass', 'NNS': 'Noun, plural', 'NNP': 'Proper noun, singular', 'NNPS': 'Proper noun, plural', 'PDT': 'Predeterminer',
    'POS': 'Possessive ending', 'PRP': 'Personal pronoun', 'PRP$': 'Possessive pronoun', 'RB': 'Adverb', 'RBR': 'Adverb, comparative', 'RBS': 'Adverb, superlative', 'RP': 'Particle', 'SYM': 'Symbol', 'TO': 'to', 'UH': 'Interjection',
    'VB': 'Verb, base form', 'VBD': 'Verb, past tense', 'VBG': 'Verb, gerund or present participle', 'VBN': 'Verb, past participle', 'VBP': 'Verb, non-3rd person singular present', 'VBZ': 'Verb, 3rd person singular present',
    'WDT': 'Wh-determiner', 'WP': 'Wh-pronoun', 'WP$': 'Possessive wh-pronoun', 'WRB': 'Wh-adverb', ':': ':', '.': '.', ';': ';', ',': ',', '?': '?', '!': '!', '(': '(', ')': ')'
}


class PartOfSpeechDataset:
    def __init__(self, idx_to_word, word_to_idx, idx_to_tag, tag_to_idx, sentences):
        self.idx_to_word = idx_to_word
        self.word_to_idx = word_to_idx
        self.idx_to_tag = idx_to_tag
        self.tag_to_idx = tag_to_idx
        self.sentences = sentences


class PartOfSpeechTagger:
    def __init__(self):
        self.hmm_ = None
        self.word_to_idx_ = None
        self.idx_to_tag_ = None


    def load_pos_dataset(self, filepath):
        def map_sentence(s):
            return [line.split(' ')[0:2] for line in s]


        with open(filepath, 'r') as f:
            contents: str = f.read().lower()
            contents = re.sub(r'\d+', r'<num>', contents)
            lines = contents.splitlines()
        sentences = [[]]
        for x in lines:
            if len(x.strip()) == 0:
                sentences.append([])
            else:
                sentences[-1].append(x)

        del lines, contents

        if len(sentences[-1]) == 0:
            sentences = sentences[:-1]

        sentences = [map_sentence(s) for s in sentences]

        words = set()
        tags = set()

        for sentence in sentences:
            for word, tag in sentence:
                words.add(word)
                tags.add(tag)

        idx_to_word = dict(enumerate(sorted(words)))
        word_to_idx = dict((word, idx) for idx, word in idx_to_word.items())
        idx_to_tag = dict(enumerate(sorted(tags)))
        tag_to_idx = dict((tag, idx) for idx, tag in idx_to_tag.items())

        return PartOfSpeechDataset(idx_to_word, word_to_idx, idx_to_tag, tag_to_idx, sentences)


    def fit(self, dataset: PartOfSpeechDataset):
        self.word_to_idx_ = dataset.word_to_idx
        self.idx_to_tag_ = dataset.idx_to_tag

        x = np.array([dataset.word_to_idx[word] for sentence in dataset.sentences for word, _ in sentence], dtype=np.int)
        y = np.array([dataset.tag_to_idx[tag] for sentence in dataset.sentences for _, tag in sentence], dtype=np.int)
        l = np.array([len(sentence) for sentence in dataset.sentences])

        self.hmm_ = HMM(len(dataset.idx_to_tag), len(dataset.idx_to_word))
        self.hmm_.fit(x, y, l)

        return self


    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self.__dict__, f)


    @classmethod
    def load(cls, path):
        with open(path, 'rb') as f:
            tagger = cls()
            tagger.__dict__ = pickle.load(f)
            return tagger


    def tokenize(self, sentence):
        sentence = re.sub(r"([.,:!?])", r" \1", sentence)
        sentence = re.sub(r'[^a-zA-Z0-9.,:;!?\s]', '', sentence)
        sentence = re.sub(r'\d+', r'<num>', sentence)
        return sentence.lower().split(' ')


    def tag(self, sentence: str, human_readable: bool = False):
        words = self.tokenize(sentence)
        words = [self.word_to_idx_[word] for word in words if word != '']
        tagged = self.hmm_.predict(np.array(words))
        tags = [self.idx_to_tag_[tag] for tag in tagged]

        if human_readable:
            return [TAGNAMES[tag.upper()] for tag in tags]
        else:
            return tags
