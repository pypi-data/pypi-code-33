
import inspect

from IPython.display import display, Markdown, Latex

from tsundoku.word2vec import Text, Word2VecText

##############################################################
# class Text(Dataset)
##############################################################

text_dataset_vectorize = '''
We can use the [`gensim.Dictionary.doc2idx`](https://radimrehurek.com/gensim/corpora/dictionary.html#gensim.corpora.dictionary.Dictionary.doc2idx) to **convert the tokenized sentence/document into a list of indices from the vocabulary**?

So the `vectorize()` would call the `Dictionary.doc2idx()` and the __getitem__ would simply wrap it into a dictionary and look like this:
'''

text_dataset_vectorize_code = '''
<br>
```python
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
```
'''

text_dataset_vectorize_code_full = '''\n<br>\n```python\n{}\n```'''.format(inspect.getsource(Text))

def hint_dataset_vectorize():
    display(Markdown("## Hint for  `class Text(Dataset)`<br>"))
    display(Markdown(text_dataset_vectorize))

def code_text_dataset_vectorize():
    display(Markdown("## Code for  `class Text(Dataset)`<br>"))
    display(Markdown(text_dataset_vectorize_code))

def full_code_text_dataset_vectorize():
    display(Markdown(text_dataset_vectorize_code_full))

##############################################################
# Word2Vec Dataset.
##############################################################

# Puts the function into the Word2VecText Dataset object.
word2vec_dataset='''
Simply reuse the `cbow_iterator()` and `skipgram_iterator()` and add it to the `Word2VecText` class. Then in the initialization, we add the variant and window size appropriately, i.e.
<br>
```python

```
Additionally, when in the `__getitem__()`, we want to first vectorize the sentence of the specific index with `self.vectorize(self.sents[index])`, then call the appropriate iterator and return the list.
<br>
```python
    def __getitem__(self, index):
        """
        The primary entry point for PyTorch datasets.
        This is were you access the specific data row you want.

        :param index: Index to the data point.
        :type index: int
        """
        vectorized_sent = self.vectorize(self.sents[index])
        return list(self._iterator(vectorized_sent))

    def vectorize(self, tokens):
        """
        :param tokens: Tokens that should be vectorized.
        :type tokens: list(str)
        """
        return self.vocab.doc2idx(tokens)
```
'''

word2vec_dataset_code_full = '''\n<br>\n```python\n{}\n```'''.format(inspect.getsource(Word2VecText))

def hint_word2vec_dataset():
    display(Markdown(word2vec_dataset))

def full_code_word2vec_dataset():
    display(Markdown(word2vec_dataset_code_full))

__all__ = [
'Text', 'hint_dataset_vectorize', 'code_text_dataset_vectorize',
'full_code_text_dataset_vectorize',
'Word2VecText', 'hint_word2vec_dataset', 'full_code_word2vec_dataset'
]
