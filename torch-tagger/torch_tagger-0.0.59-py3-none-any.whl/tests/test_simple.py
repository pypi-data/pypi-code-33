import pickle
import unittest

from torch_tagger import Tagger


class TestSimple(unittest.TestCase):
    def test_simple(self):
        texts = [
            'I want fly to New York',
            'Let me book a hotel in Tokyo',
            'What is the time in Beijing ?',
            'the weather in Beijing and New York ?',
        ]
        labels = [
            'O O O O B-City E-City',
            'O O O O O O S-City',
            'O O O O O S-City O',
            'O O O S-City O B-City E-City O',
        ]

        texts = [x.split() for x in texts]
        labels = [x.split() for x in labels]

        tag = Tagger(batch_size=2, verbose=0, epochs=100)
        tag.fit(texts, labels)

        precision, recall, f1score = tag.score(texts, labels, detail=True)

        self.assertEqual(precision, 1.0)
        self.assertEqual(recall, 1.0)
        self.assertEqual(f1score, 1.0)

        self.assertEqual(tag.predict([texts[0]])[0], labels[0])

        self.assertEqual(
            tag.predict(['the weather in Beijing and New York ?'.split()])[0],
            'O O O S-City O B-City E-City O'.split())

        with open('/tmp/torch-tagger-tmp.pkl', 'wb') as fp:
            pickle.dump(tag, fp)

        with open('/tmp/torch-tagger-tmp.pkl', 'rb') as fp:
            tag = pickle.load(fp)

        self.assertEqual(
            tag.predict(['the weather in Beijing and New York ?'.split()])[0],
            'O O O S-City O B-City E-City O'.split())


if __name__ == '__main__':
    unittest.main()
