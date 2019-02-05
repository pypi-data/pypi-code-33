# -*- coding: utf-8 -*-
"""Classes and functions to evaluate embeddings according to a text classification task

"""
import collections
import itertools

import numpy as np

import sklearn

import mangoes
from mangoes.evaluation.base import PrintableReport, BaseEvaluation, BaseEvaluator


# ####################################################################################################################
# DATASETS

_Document = collections.namedtuple("Document", "sentence label")

class Dataset(mangoes.evaluation.base.BaseDataset):
    """Class to create a Dataset of classification, to be used in Evaluation class

    Examples
    --------
    >>> from mangoes.evaluation.text_classification import Dataset
    >>> user_dataset = Dataset("user dataset", ['"Now all @Apple has to do is get swype on the iphone and it will be crack. Iphone that is" positive',
    ...                                         '"removing all @apple shit." negative'])
    >>> tweets = Dataset("tweets", "../resources/en/text_classification/sanders-twitter-full-corpus.csv")

     datasets are available in this module:

    - the TWITTER dataset :
    >>> import mangoes.evaluation.text_classification
    >>> twitter = mangoes.evaluation.text_classification.TWITTER
    """
    @classmethod
    def parse_question(cls, question):
        """
        Examples
        --------
        >>> Dataset.parse_question('"apple","positive","126415614616154112","Tue Oct 18 21:53:25 +0000 2011","Now all @Apple has to do is get swype on the iphone and it will be crack. Iphone that is"')
        Document(sentence='Now all @Apple has to do is get swype on the iphone and it will be crack. Iphone that is', label='positive')

        Parameters
        ----------
        question: str
            A splittable string

        Returns
        -------
        namedtuple

        """
        if isinstance(question, _Document):
            return question
        return _Document(*question.split())
        # result = None
        # try:
        #     s = question.split(',')
        #     result = _Document(s[-1][1:-1], s[1][1:-1])
        # except Exception:
        #     print("question", question)
        #     # raise
        # return result

    @property
    def sentences(self):
        return [d.sentence for d in self.data if d]

    @property
    def labels(self):
        return [d.label for d in self.data if d]

    @property
    def train_dataset(self):
        return Dataset(self.name + ' train', self.data[:len(self.data)//2])

    @property
    def test_dataset(self):
        return Dataset(self.name + ' test', self.data[len(self.data)//2:])


TWITTER = Dataset("Twitter", "../resources/en/text_classification/sanders-twitter-full-corpus.csv")

# ####################################################################################################################
# EVALUATOR

class Evaluator(BaseEvaluator):
    def __init__(self, representation, train_dataset, k=None):
        self.representation = representation
        self.train_dataset = train_dataset

        distances = self.get_train_distances()
        self.k = k if k else self.tune_k(distances, train_dataset.labels)
        self.classifier = sklearn.neighbors.KNeighborsClassifier(self.k, metric='precomputed')
        self.classifier.fit(distances, train_dataset.labels)
        del distances

    def tune_k(self, distances, labels):
        gs_knn = sklearn.neighbors.KNeighborsClassifier(metric='precomputed')
        gs_clf = sklearn.model_selection.GridSearchCV(gs_knn, {'n_neighbors': range(1, 20)})
        gs_clf.fit(distances, labels)
        return gs_clf.best_params_['n_neighbors']

    def get_train_distances(self, metric="euclidean"):
        sentences = self.train_dataset.sentences
        distances = np.zeros((len(sentences), len(sentences)))
        nb_sentence = len(sentences)
        for i, j in itertools.combinations(range(nb_sentence), 2):
            d = self.representation.word_mover_distance(sentences[i], sentences[j], metric=metric)
            distances[i, j] = d
            distances[j, i] = d

        return distances

    def get_test_distances(self, test_sentences, train_sentences, metric="euclidean"):
        test_distances = np.zeros((len(test_sentences), len(train_sentences)))

        for i, s1 in enumerate(test_sentences):
            for j, s2 in enumerate(train_sentences):
                test_distances[i, j] = self.representation.word_mover_distance(s1, s2, metric=metric)

        return test_distances

    def predict(self, document):
        """Predict the class for the given document.

        Examples
        --------
        >>> # create a representation
        >>> import numpy as np
        >>> import mangoes
        >>> vocabulary = mangoes.Vocabulary(['paris', 'london', 'brussels', 'madrid', 'roma',
        ...                                  'england', 'belgium', 'germany', 'spain', 'italy'])
        >>> matrix = np.array([[1, 0], [1, 0.2], [1, 0.1], [0.9, 0], [0.9, 0.1],
        ...                    [0, 1.2], [0, 1], [0, 1.1], [0.1, 1], [0.1, 0.9]])
        >>> representation = mangoes.Embeddings(vocabulary, matrix)
        >>> # predict
        >>> import mangoes.evaluation.text_classification
        >>> dataset = mangoes.evaluation.text_classification.Dataset('test', ['paris capital', 'london capital',
        ...                                                                   'england country', 'belgium country',
        ...                                                                   'madrid capital', 'spain germany'])
        >>> evaluator = mangoes.evaluation.text_classification.Evaluator(representation, dataset, k=4)
        >>> evaluator.predict('brussels')[0]
        'capital'
        """
        if isinstance(document, str):
            document = [document]
        distances = self.get_test_distances(document, self.train_dataset.sentences)
        predictions = self.classifier.predict(distances)
        return {d: p for d, p in zip(document, predictions)}

    def score(self, data):
        distances = self.get_test_distances(data.sentences, self.train_dataset.sentences)
        return self.classifier.score(distances, data.labels)


# ####################################################################################################################
# EVALUATION

class Evaluation(BaseEvaluation):
    """
    Examples
    --------
    >>> # create a representation
    >>> import numpy as np
    >>> import mangoes
    >>> vocabulary = mangoes.Vocabulary(['paris', 'london', 'brussels', 'madrid', 'roma',
    ...                                  'england', 'belgium', 'germany', 'spain', 'italy'])
    >>> matrix = np.array([[1, 0], [1, 0.2], [1, 0.1], [0.9, 0], [0.9, 0.1],
    ...                    [0, 1.2], [0, 1], [0, 1.1], [0.1, 1], [0.1, 0.9]])
    >>> representation = mangoes.Embeddings(vocabulary, matrix)
    >>> import mangoes.evaluation.text_classification
    >>> # evaluate
    >>> dataset = mangoes.evaluation.text_classification.Dataset('test', ['paris capital', 'london capital',
    ...                                                                   'england country', 'belgium country',
    ...                                                                   'madrid capital', 'spain country'])
    >>> evaluation = mangoes.evaluation.text_classification.Evaluation(representation, dataset, k=3)
    >>> print(evaluation.get_score())
    Score(accuracy=0.5, nb=3)
    >>> print(evaluation.get_report(show_questions=True)) # doctest: +NORMALIZE_WHITESPACE
                                                                Nb questions         OPP    accuracy
    ================================================================================================
    test                                                                 2/2     100.00%     100.00%
    ------------------------------------------------------------------------------------------------
    """
    _Score = collections.namedtuple("Score", "accuracy nb")

    class _Report(PrintableReport):
        HEADER = [(("Nb questions", "accuracy"), (3, 3))]
        PREDICTION_HEADER = [(("gold", "prediction",), (3, 3))]

        def _print_score(self, score):
            if score.nb:
                return "{:>{width}}".format("{:.2%}".format(score.accuracy),
                                                       width=3 * self.COL)
            else:
                return "{:>{width}}".format('NA', width=3 * self.COL)

        def _print_prediction(self, document, indent):
            prediction = self.evaluation.predictions[document.sentence]
            line = "{:{width}}".format('    ' * indent + document.sentence, width=(self.LINE_LENGTH - 6 * self.COL))
            line += "{:>{width}}".format(document.label, width=3 * self.COL)
            line += "{:>{width}}".format(prediction, width=3 * self.COL)
            return line + "\n"

    def __init__(self, representation, dataset, lower=True, k=None):
        super(Evaluation, self).__init__(Evaluator(representation, dataset.train_dataset, k=k), dataset.test_dataset, lower=lower)

    def get_score(self, dataset=None, keep_duplicates=True):
        return self._Score(self.evaluator.score(self.datasets[0].test_dataset),
                           len(self._questions_by_subset[self.datasets[0].name].questions))

    def _filter_list_of_questions(self, list_of_questions):
        subset_documents = []  # documents that can be predicted, respecting duplicates and order from original
        unique_documents = set()  # unique documents to classify
        unique_documents_with_label = set()  # unique documents with expected labels to detect duplicates
        nb_oov = 0  # number of ignored analogies due to OOV terms
        nb_duplicates = 0  # number of duplicates among the filtered analogies

        for document in list_of_questions:
            document = _Document(document.sentence.lower(), document.label) if self.lower else document

            if all(w in self.evaluator.representation.words for w in document.sentence.split()): # TODO: not sure they all have to be
                subset_documents.append(document)

                if document in unique_documents_with_label:
                    nb_duplicates += 1
                else:
                    unique_documents_with_label.add(document)
                unique_documents.add(document.sentence)
            else:
                nb_oov += 1

        result = self._FilteredSubset(subset_documents, len(list_of_questions), nb_oov, nb_duplicates)
        return result, unique_documents, unique_documents_with_label

# ###########################
# # TUNING DE K
# ###########################
# if not k:
#     gs_knn = sklearn.neighbors.KNeighborsClassifier(metric='precomputed')
#     gs_clf = sklearn.model_selection.GridSearchCV(gs_knn, {'n_neighbors': range(1, 20)})
#     gs_clf.fit(distances, y_train)
#     print("\n\n K : " + str(gs_clf.best_params_['n_neighbors']) + '\n\n')
#     k = gs_clf.best_params_['n_neighbors']
#
#
# ###########################
# # CLASSIFICATION
# ###########################
# clf = sklearn.neighbors.KNeighborsClassifier(k, metric='precomputed')
# clf.fit(distances, y_train)
#
# score = clf.score(test_distances, y_test)
# print(score)
#
# with open('results.txt', mode='a') as f:
#     import time
#     timestr = time.strftime("%Y-%m-%d-%Hh%Mm%Ss")
#     f.write('{}\t{}\t{}\t{}\t{}\t{}\n'.format(timestr, dataset, embeddings_name, metric, k, score))
#
# # print(clf.predict(test_distances))
# # print(y_test)

#
# import itertools
# import logging
# import multiprocessing
# import string
# import time
#
# import numpy as np
# import sklearn.datasets
# import sklearn.model_selection
# import sklearn.neighbors
# import tqdm
#
# import mangoes
#
# logging_level = logging.DEBUG
# logging_format = '%(asctime)s :: %(name)s::%(funcName)s() :: %(levelname)s :: %(message)s'
# logging.basicConfig(level=logging_level, format=logging_format, filename="report.log")
# logger = logging.getLogger(__name__)
#
# # embeddings = ('mg_win2_200', './representations/ppmi_svd_wiki_en_tok_WIN_2_alpha_0.75_dim_200_eig_0/')
# # embeddings = ('mg_win2_1000', './representations/ppmi_svd_wiki_en_tok_WIN_2_alpha_0.75_dim_1000_eig_0')
# # embeddings = ('mg_win2_sparse', './representations/ppmi_wiki_en_tok_WIN_2_alpha_0.75')
#
# # embeddings = ('mg_win5_200', './representations/ppmi_svd_wiki_en_tok_WIN_5_alpha_0.75_dim_200_eig_0')
# # embeddings = ('mg_win5_1000', './representations/ppmi_svd_wiki_en_tok_WIN_5_alpha_0.75_dim_1000_eig_0')
#
# # embeddings = ('mg_DBC_200', './representations/ppmi_svd_wiki_en_conllu_DBC_labels_False_collapse_False_alpha_0.75_dim_200_eig_0')
# # embeddings = ('mg_DBC_500', './representations/ppmi_svd_wiki_en_conllu_DBC_labels_False_collapse_False_alpha_0.75_dim_500')
# # embeddings = ('mg_DBC_labels_500', './representations/ppmi_svd_wiki_en_conllu_DBC_labels_True_collapse_False_alpha_0.75_dim_500')
#
# embeddings = ('w2v_GoogleNews', 'GoogleNews-vectors_from_w2v')
#
#
# embeddings_name, embeddings_path = embeddings
#
# dataset = "twitter"
# # dataset = "bbcsport"
# # dataset = "20news"
# # dataset = "reuters"
# # dataset = "ohsumed"
#
# metric = "euclidean"
# # metric = "cosine"
# # metric = "manhattan"
#
# emd = "POT"
# # emd = "pyemd"
#
#
# k = None#5 # None -> tuné avec GridSearch
#
# nb_processes = 12
#
#
# def smart_stopwords():
#     stopwords = []
#     with open('SmartStoplist.txt') as f:
#         f.readline()
#         for line in f:
#             stopwords.append(line.strip())
#     return stopwords
#
#
# # stopwords = nltk.corpus.stopwords.words('english')
# stopwords = smart_stopwords()
#
#
# def print_info(documents, classes, comment, training=False):
#     print("\n\nNb d'inputs dans le {} ({}) : {}".format('training set' if training else 'dataset', comment,
#                                                         len(documents)))
#     print("Nb de mots uniques total : {}".format(len({w for s in documents for w in s.split()})))
#     print("Nb de mots uniques par document (avg) : {:.3f}".format(np.mean([len(set(s.split())) for s in documents])))
#     print("Nb de classes : {}".format(len(set(classes))))
#
#
# def load_dataset(dataset):
#     def load_bbcsport():
#         bbcsport = sklearn.datasets.load_files('bbcsport/')
#
#         documents, classes = bbcsport.data, bbcsport.target
#         print_info(documents, classes, "avant suppression des stopwords et oov")
#
#         documents = [remove_stopwords(remove_punctuation(str(d.replace(b'\n', b' '))).lower()) for d in documents]
#         print_info(documents, classes, "après suppression des stopwords et ponctuation")
#
#         return sklearn.model_selection.train_test_split(documents, classes, train_size=517)#, random_state=0)
#
#     def load_twitter():
#         import csv
#         tweets = []
#         sentiments = []
#
#         with open('sanders-twitter-full-corpus.csv') as csvfile:
#             reader = csv.reader(csvfile, quotechar='"')
#             reader.__next__() # remove header
#             for row in reader:
#                 sentiment = row[1]
#                 if sentiment != "irrelevant":
#                     tweets.append(row[-1])
#                     sentiments.append(sentiment)
#         print_info(tweets, sentiments, "avant suppression des stopwords et oov")
#
#         tweets = [remove_stopwords(remove_punctuation(d).lower()) for d in tweets]
#         print_info(tweets, sentiments, "après suppression des stopwords et ponctuation")
#
#         return sklearn.model_selection.train_test_split(tweets, sentiments, train_size=2176)#, random_state=0) #2176
#
#     def load_20news():
#         sentences_train, classes_train = [], []
#         sentences_test, classes_test = [], []
#
#         with open('20news/20ng-train-all-terms.txt') as f:
#             for row in f:
#                 c, s = row.split('\t')
#                 sentences_train.append(remove_stopwords(s))
#                 classes_train.append(c)
#
#         with open('20news/20ng-test-all-terms.txt') as f:
#             for row in f:
#                 c, s = row.split('\t')
#                 sentences_test.append(remove_stopwords(s))
#                 classes_test.append(c)
#
#         print_info(sentences_train, classes_train, "après suppression des stopwords", training=True)
#
#         # remove all words that appear less than 5 times across all documents
#         train_corpus = mangoes.Corpus(sentences_train + sentences_test)
#         more_than_5_times_vocabulary = train_corpus.create_vocabulary(filters=[mangoes.corpus.remove_least_frequent(4)])
#
#         sentences_train = [remove_oov(s, more_than_5_times_vocabulary) for s in sentences_train]
#         sentences_test = [remove_oov(s, more_than_5_times_vocabulary) for s in sentences_test]
#         print_info(sentences_train, classes_train, "après suppression des mots rares (< 5)", training=True)
#
#         # limit all documents to the most common 500 words in each documents
#         sentences_train_500 = []
#         for s in sentences_train:
#             s_sorted = sorted(s.split(), key=lambda w: train_corpus.words_count[w], reverse=True)
#             sentences_train_500.append(' '.join(s_sorted[:500]))
#         print_info(sentences_train_500, classes_train, "après limitation aux 500 mots les plus fréquents", training=True)
#
#         sentences_test_500 = []
#         for s in sentences_test:
#             s_sorted = sorted(s.split(), key=lambda w: train_corpus.words_count[w], reverse=True)
#             sentences_test_500.append(' '.join(s_sorted[:500]))
#
#         return sentences_train_500, sentences_test_500, classes_train, classes_test
#
#     def load_reuters():
#         sentences_train, classes_train = [], []
#         sentences_test, classes_test = [], []
#
#         with open('reuters8/r8-train-all-terms.txt') as f:
#             for row in f:
#                 c, s = row.split('\t')
#                 sentences_train.append(remove_stopwords(s))
#                 classes_train.append(c)
#
#         with open('reuters8/r8-test-all-terms.txt') as f:
#             for row in f:
#                 c, s = row.split('\t')
#                 sentences_test.append(remove_stopwords(s))
#                 classes_test.append(c)
#
#         return sentences_train, sentences_test, classes_train, classes_test
#
#     def load_ohsumed():
#         ohsumed_train = sklearn.datasets.load_files('ohsumed-first-20000-docs/training')
#         ohsumed_test = sklearn.datasets.load_files('ohsumed-first-20000-docs/test')
#
#         sentences_train, sentences_test = ohsumed_train.data, ohsumed_test.data
#         print_info(sentences_train, ohsumed_train.target, "avant suppression des stopwords et ponctuation", training=True)
#
#         sentences_train = [remove_stopwords(str(s)) for s in sentences_train]
#         sentences_test = [remove_stopwords(str(s)) for s in sentences_test]
#         print_info(sentences_train, ohsumed_train.target, "après suppression des stopwords", training=True)
#
#         sentences_train = [remove_punctuation(str(s)) for s in sentences_train]
#         sentences_test = [remove_punctuation(str(s)) for s in sentences_test]
#         print_info(sentences_train, ohsumed_train.target, "après suppression de la ponctuation", training=True)
#
#         return sentences_train, sentences_test, ohsumed_train.target, ohsumed_test.target
#
#
#
#     if dataset == "twitter":
#         return load_twitter()
#     elif dataset == "bbcsport":
#         return load_bbcsport()
#     elif dataset == "20news":
#         return load_20news()
#     elif dataset == "reuters":
#         return load_reuters()
#     elif dataset == "ohsumed":
#         return load_ohsumed()
#
#
# def remove_stopwords(sentence):
#     return ' '.join([w for w in sentence.split() if w not in stopwords])
#
#
# def remove_punctuation(sentence):
#     for p in string.punctuation:
#         sentence = sentence.replace(p, ' ')
#     return sentence
#
#
# def remove_oov(sentence, vocabulary):
#     return ' '.join([w for w in sentence.split() if w in vocabulary])
#
#
# def prune_empty(dataset):
#     sentences, classes = dataset
#     return [s for s in sentences if s], [c for c, s in zip(classes, sentences) if s]
#
#
# def get_train_distances(sentences, representation, metric="euclidean"):
#     distances = np.zeros((len(sentences), len(sentences)))
#
#     print("\n\ndistances pour training : {}\n".format(distances.shape))
#
#     nb_sentence = len(sentences)
#     for i, j in tqdm.tqdm(itertools.combinations(range(nb_sentence), 2), total=(nb_sentence*(nb_sentence-1))/2):
#         d = representation.word_mover_distance(sentences[i], sentences[j], metric=metric, emd="POT")
#         distances[i, j] = d
#         distances[j, i] = d
#
#     return distances
#
# def get_test_distances(test_sentences, train_sentences, representation, metric="euclidean"):
#     test_distances = np.zeros((len(test_sentences), len(train_sentences)))
#
#     print("\n\ndistances pour testing : {}\n".format(test_distances.shape))
#     for i, s1 in tqdm.tqdm(enumerate(test_sentences), total=len(test_sentences)):
#         for j, s2 in tqdm.tqdm(enumerate(train_sentences), total=len(train_sentences)):
#             test_distances[i, j] = representation.word_mover_distance(s1, s2, metric=metric, emd="POT")
#
#     return test_distances
#
#
# def worker(task_queue, done_queue, representation, metric):
#     print("lancement worker")
#     while True:
#         try:
#             (i, first_sentence), (j, second_sentence) = task_queue.get()
#             done_queue.put((i, j, representation.word_mover_distance(first_sentence, second_sentence, metric=metric)))
#         except TypeError:
#             break
#     print("fin worker")
#
# ## Parallel avec process
# def get_train_distances_parallel(sentences, representation, metric="euclidean"):
#     print("\n\ndistances pour training\n")
#
#     task_queue = multiprocessing.Queue(maxsize=2000)
#     done_queue = multiprocessing.Queue()
#
#     pool = [multiprocessing.Process(target=worker, args=(task_queue, done_queue, representation, metric))
#             for _ in range(nb_processes - 1)]
#     pool.append(multiprocessing.Process(target=feed_worker_for_train, args=(sentences, task_queue, nb_processes - 1)))
#
#     for p in pool:
#         p.start()
#
#     nb_sentence = len(sentences)
#     nb_pairs = (nb_sentence * (nb_sentence - 1)) // 2
#     distances = np.zeros((len(sentences), len(sentences)))
#
#     for _ in tqdm.trange(nb_pairs):
#         i, j, d = done_queue.get()
#         distances[i,j] = d
#         distances[j,i] = d
#
#     for p in pool:
#         p.join()
#
#     return distances
#
# def get_test_distances_parallel(test_sentences, train_sentences, representation, metric="euclidean"):
#     print("\n\ndistances pour test\n")
#
#     task_queue = multiprocessing.Queue(maxsize=2000)
#     done_queue = multiprocessing.Queue()
#
#     pool = [multiprocessing.Process(target=worker, args=(task_queue, done_queue, representation, metric))
#             for _ in range(nb_processes - 1)]
#     pool.append(multiprocessing.Process(target=feed_worker_for_test, args=(test_sentences, train_sentences, task_queue, nb_processes - 1)))
#
#     for p in pool:
#         p.start()
#
#     distances = np.zeros((len(test_sentences), len(train_sentences)))
#
#     for _ in tqdm.trange(len(test_sentences)*len(train_sentences)):
#         i, j, d = done_queue.get()
#         distances[i,j] = d
#
#     for p in pool:
#         p.join()
#
#     return distances
#
# def feed_worker_for_train(sentences, task_queue, nb_sentinel):
#     for i, j in itertools.combinations(range(len(sentences)), 2):
#         task_queue.put(((i, sentences[i]), (j, sentences[j])))
#
#     for _ in range(nb_sentinel):
#         task_queue.put(None)
#
# def feed_worker_for_test(test_sentences, train_sentences, task_queue, nb_sentinel):
#     for i, j in itertools.product(range(len(test_sentences)), range(len(train_sentences))):
#         task_queue.put(((i, test_sentences[i]), (j, train_sentences[j])))
#
#     for _ in range(nb_sentinel):
#         task_queue.put(None)
#
#
# ## Parallel avec Pool
# import functools
# def worker2(pair, representation, metric, sentences):
#     i, j = pair
#     first_sentence, second_sentence = sentences[i], sentences[j]
#     return i, j, representation.word_mover_distance(first_sentence, second_sentence, metric=metric)
#
#
# def get_train_distances_parallel2(sentences, representation, metric="euclidean"):
#     print("\n\ndistances pour train\n")
#
#     c_worker = functools.partial(worker2, representation=representation, metric=metric)
#     pool = multiprocessing.Pool(nb_processes)
#
#     distances = np.zeros((len(sentences), len(sentences)))
#     # for i, j, d in tqdm.tqdm(pool.imap_unordered(c_worker, itertools.combinations(range(len(sentences)), 2))):
#     for i, j, d in pool.map_async(c_worker, itertools.combinations(range(len(sentences)), 2)):
#         distances[i,j] = d
#         distances[j,i] = d
#
#     return distances
#
#
# ## Parallel avec mangoes.multiproc
# import signal
# class Timeout():
#     """Timeout class using ALARM signal."""
#
#     class Timeout(Exception):
#         pass
#
#     def __init__(self, sec):
#         self.sec = sec
#
#     def __enter__(self):
#         signal.signal(signal.SIGALRM, self.raise_timeout)
#         signal.alarm(self.sec)
#
#     def __exit__(self, *args):
#         signal.alarm(0)  # disable alarm
#
#     def raise_timeout(self, *args):
#         raise Timeout.Timeout()
#
# def _train_distances(pairs, sentences, representation, metric, nb_pairs):
#     result = []
#     with tqdm.tqdm(total=nb_pairs) as progress_bar:
#         for i, j in pairs:
#             try:
#                 with Timeout(3):
#                     result.append((i, j, representation.word_mover_distance(sentences[i],
#                                                                             sentences[j],
#                                                                             metric=metric)))
#             except Timeout.Timeout:
#                 logging.debug("Timeout train pour i=%s (%s) et j=%s (%s)", i, sentences[i], j, sentences[j])
#                 result.append((i, j, -1))
#             progress_bar.update()
#     return result
#
# def _test_distances(pairs, test_sentences, train_sentences, representation, metric, nb_pairs):
#     result = []
#     print("nb de pairs par process : ", nb_pairs)
#     with tqdm.tqdm() as progress_bar: #
#         for i, j in pairs:
#             try:
#                 with Timeout(3):
#                     result.append((i, j, representation.word_mover_distance(test_sentences[i],
#                                                                             train_sentences[j],
#                                                                             metric=metric)))
#             except Timeout.Timeout:
#                 logging.debug("Timeout test pour i=%s (%s) et j=%s (%s)", i, test_sentences[i], j, train_sentences[j])
#                 result.append((i, j, -1))
#             progress_bar.update()
#     return result
#
# def _reduce(total, part):
#     total.extend(part)
#     return total
#
# def get_train_distances_parallel3(sentences, representation, metric="euclidean"):
#     print("\n\ndistances pour train\n")
#
#     data_parallel = mangoes.utils.multiproc.DataParallel(_train_distances,
#                                                          _reduce,
#                                                          nb_workers=nb_processes)
#
#     pairs = itertools.combinations(range(len(sentences)), 2)
#     nb_pairs_per_process = (len(sentences)*(len(sentences)-1)//2)//(nb_processes - 1)
#     result = data_parallel.run(pairs, *(sentences, representation, metric, nb_pairs_per_process))
#
#     distances = np.zeros((len(sentences), len(sentences)))
#     for i, j, d in result:
#         distances[i,j] = d
#         distances[j,i] = d
#
#     return distances
#
# def get_test_distances_parallel3(test_sentences, train_sentences, representation, metric="euclidean"):
#     print("\n\ndistances pour test\n")
#
#     data_parallel = mangoes.utils.multiproc.DataParallel(_test_distances,
#                                                          _reduce,
#                                                          nb_workers=nb_processes)
#
#     pairs = itertools.product(range(len(test_sentences)), range(len(train_sentences)))
#     nb_pairs_per_process = len(test_sentences)*len(train_sentences)//(nb_processes - 1)
#     result = data_parallel.run(pairs, *(test_sentences, train_sentences, representation, metric, nb_pairs_per_process))
#
#     distances = np.zeros((len(test_sentences), len(train_sentences)))
#     for i, j, d in result:
#         distances[i,j] = d
#
#     return distances
#
# print("Dataset = " + dataset)
# print("Embeddings = " + embeddings_name)
# print("Metric = " + metric)
# print('\n')
#
#
# ###########################
# # CHARGEMENT DU DATASET
# ###########################
# X_train, X_test, y_train, y_test = load_dataset(dataset)
# print_info(X_train, y_train, "avant suppression des oov", training=True)
#
#
# ###########################
# # CHARGEMENT DE L'EMBEDDING
# ###########################
# representation = mangoes.Embeddings.load(embeddings_path)
#
#
# ###########################
# # OOV
# ###########################
# X_train, y_train = prune_empty(([remove_oov(s, representation.words) for s in X_train], y_train))
# X_test, y_test = prune_empty(([remove_oov(s, representation.words) for s in X_test], y_test))
# print_info(X_train, y_train, "après suppression des oov", training=True)
#
# print('\n')
#
# # X_train = X_train[:1000]
# # y_train = y_train[:1000]
# #
# # X_test = X_test[:100]
# # y_test = y_test[:100]
#
# ###########################
# # CALCUL DES DISTANCES
# ###########################
# train_distances_path = 'train_distances_{}_{}_{}.npy'.format(dataset, embeddings_name, metric)
# test_distances_path = 'test_distances_{}_{}_{}.npy'.format(dataset, embeddings_name, metric)
#
# if dataset in ["bbcsport", "twitter"]:
#     distances = get_train_distances_parallel3(X_train, representation, metric=metric)
#     test_distances = get_test_distances_parallel3(X_test, X_train, representation, metric=metric)
# else:
#     try:
#         distances = np.load(train_distances_path)
#     except FileNotFoundError:
#         distances = get_train_distances_parallel3(X_train, representation, metric=metric)
#         np.save(train_distances_path, distances)
#
#     try:
#         test_distances = np.load(test_distances_path)
#     except FileNotFoundError:
#         start = 0
#         test_distances = np.zeros((len(X_test), len(X_train)))
#         while start < len(X_test):
#             end = min(start + 100, len(X_test))
#             test_distances_part = get_test_distances_parallel3(X_test[start:end], X_train, representation, metric=metric)
#             np.save(test_distances_path + '_{}_{}'.format(start, end), test_distances_part)
#
#             test_distances += test_distances_path
#             start = end
#         np.save(test_distances_path, test_distances)
#
#
#
# ###########################
# # TUNING DE K
# ###########################
# if not k:
#     gs_knn = sklearn.neighbors.KNeighborsClassifier(metric='precomputed')
#     gs_clf = sklearn.model_selection.GridSearchCV(gs_knn, {'n_neighbors': range(1, 20)})
#     gs_clf.fit(distances, y_train)
#     print("\n\n K : " + str(gs_clf.best_params_['n_neighbors']) + '\n\n')
#     k = gs_clf.best_params_['n_neighbors']
#
#
# ###########################
# # CLASSIFICATION
# ###########################
# clf = sklearn.neighbors.KNeighborsClassifier(k, metric='precomputed')
# clf.fit(distances, y_train)
#
# score = clf.score(test_distances, y_test)
# print(score)
#
# with open('results.txt', mode='a') as f:
#     import time
#     timestr = time.strftime("%Y-%m-%d-%Hh%Mm%Ss")
#     f.write('{}\t{}\t{}\t{}\t{}\t{}\n'.format(timestr, dataset, embeddings_name, metric, k, score))
#
# # print(clf.predict(test_distances))
# # print(y_test)
#
#
#
#
#
