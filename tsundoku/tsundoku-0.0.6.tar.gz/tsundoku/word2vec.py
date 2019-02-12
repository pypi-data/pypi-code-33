from IPython.display import display, Markdown, Latex

##############################################################
# class Text(Dataset)
##############################################################
from gensim.corpora import Dictionary
from torch.utils.data import Dataset, DataLoader

class Text(Dataset):
    def __init__(self, tokenized_texts):
        """
        :param tokenized_texts: Tokenized text.
        :type tokenized_texts: list(list(str))
        """
        self.sents = tokenized_texts
        self.vocab = Dictionary(tokenized_texts)

    def __getitem__(self, index):
        """
        The primary entry point for PyTorch datasets.
        This is were you access the specific data row you want.

        :param index: Index to the data point.
        :type index: int
        """
        # Hint: You want to return a vectorized sentence here.
        return {'x': self.vectorize(self.sents[index])}

    def vectorize(self, tokens):
        """
        :param tokens: Tokens that should be vectorized.
        :type tokens: list(str)
        """
        # See https://radimrehurek.com/gensim/corpora/dictionary.html#gensim.corpora.dictionary.Dictionary.doc2idx
        return self.vocab.doc2idx(tokens)

    def unvectorize(self, indices):
        """
        :param indices: Converts the indices back to tokens.
        :type tokens: list(int)
        """
        return [self.vocab[i] for i in indices]



##############################################################
# Word2Vec Dataset.
##############################################################

from functools import partial
from torch.utils.data import Dataset, DataLoader
from torch import functional as F

def per_window(sequence, n=1):
    """
    From http://stackoverflow.com/q/42220614/610569
        >>> list(per_window([1,2,3,4], n=2))
        [(1, 2), (2, 3), (3, 4)]
        >>> list(per_window([1,2,3,4], n=3))
        [(1, 2, 3), (2, 3, 4)]
    """
    start, stop = 0, n
    seq = list(sequence)
    while stop <= len(seq):
        yield seq[start:stop]
        start += 1
        stop += 1


class Word2VecText(Dataset):
    def __init__(self, tokenized_texts, window_size, variant):
        """
        :param tokenized_texts: Tokenized text.
        :type tokenized_texts: list(list(str))
        """
        self.sents = tokenized_texts
        self._len = len(self.sents)
        self.vocab = Dictionary(self.sents)
        self.window_size = window_size
        self.variant = variant
        if variant.lower() == 'cbow':
            self._iterator = partial(self.cbow_iterator, window_size=self.window_size)
        elif variant.lower() == 'skipgram':
            self._iterator = partial(self.skipgram_iterator, window_size=self.window_size)

    def __getitem__(self, index):
        """
        The primary entry point for PyTorch datasets.
        This is were you access the specific data row you want.

        :param index: Index to the data point.
        :type index: int
        """
        vectorized_sent = self.vectorize(self.sents[index])
        return list(self._iterator(vectorized_sent))

    def __len__(self):
        return self._len

    def vectorize(self, tokens):
        """
        :param tokens: Tokens that should be vectorized.
        :type tokens: list(str)
        """
        # See https://radimrehurek.com/gensim/corpora/dictionary.html#gensim.corpora.dictionary.Dictionary.doc2idx
        return self.vocab.doc2idx(tokens)

    def unvectorize(self, indices):
        """
        :param indices: Converts the indices back to tokens.
        :type tokens: list(int)
        """
        return [self.vocab[i] for i in indices]

    def cbow_iterator(self, tokens, window_size):
        """
            >>> tokens = ['language', 'users', 'never', 'choose', 'words', 'randomly',
            ...           ',', 'and', 'language', 'is', 'essentially', 'non-random', '.']
            >>> cbow_iterator(tokens, 2)
            [(['language', 'users', 'choose', 'words'], 'never'),
            (['users', 'never', 'words', 'randomly'], 'choose'),
            (['never', 'choose', 'randomly', ','], 'words'),
            (['choose', 'words', ',', 'and'], 'randomly'),
            (['words', 'randomly', 'and', 'language'], ','),
            (['randomly', ',', 'language', 'is'], 'and'),
            ([',', 'and', 'is', 'essentially'], 'language'),
            (['and', 'language', 'essentially', 'non-random'], 'is'),
            (['language', 'is', 'non-random', '.'], 'essentially')]
        """
        n = window_size * 2 + 1
        for window in per_window(tokens, n):
            target = window.pop(window_size)
            yield {'x': window, 'y': target}   # X = window ; Y = target.

    def skipgram_iterator(self, tokens, window_size):
        """
            >>> tokens = ['language', 'users', 'never', 'choose', 'words', 'randomly',
            ...           ',', 'and', 'language', 'is', 'essentially', 'non-random', '.']
            >>> list(skipgram_iterator(tokens, 2))[:10]
            [('never', 'language', 1),
             ('never', 'users', 1),
             ('never', 'choose', 1),
             ('never', 'words', 1),
             ('never', 'non-random', 0),
             ('never', 'is', 0),
             ('never', 'and', 0),
             ('never', 'and', 0),
             ('choose', 'users', 1),
             ('choose', 'never', 1)]
        """
        n = window_size * 2 + 1
        for i, window in enumerate(per_window(tokens, n)):
            focus = window.pop(window_size)
            # Generate positive samples.
            for context_word in window:
                yield {'x': (focus, context_word), 'y':1}
            # Generate negative samples.
            for _ in range(n-1):
                leftovers = tokens[:i] + tokens[i+n:]
                yield {'x': (focus, random.choice(leftovers)), 'y':0}


__all__ = [
'Text',
'Word2VecText',
]
