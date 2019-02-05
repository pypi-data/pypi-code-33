import unittest

from torch_tagger import Tagger

texts = [
    '我 想 飞 到 纽 约',
    '定 个 酒 店 在 东 京',
    '北 京 现 在 什 么 时 间 ?',
    '北 京 和 纽 约 的 时 间 ?',
]
labels = [
    'O O O O B-City E-City',
    'O O O O O B-City E-City',
    'B-City E-City O O O O O O O',
    'B-City E-City O B-City E-City O O O O',
]

texts = [x.split() for x in texts]
labels = [x.split() for x in labels]


class TestSimple(unittest.TestCase):
    def test_simple_cn(self):
        tag = Tagger(batch_size=2, verbose=0, epochs=100)
        tag.fit(texts, labels)

        accuracy, recall, f1score = tag.score(texts, labels, detail=True)

        self.assertEqual(accuracy, 1.0)
        self.assertEqual(recall, 1.0)
        self.assertEqual(f1score, 1.0)

        self.assertEqual(tag.predict([texts[0]])[0], labels[0])

        self.assertEqual(
            tag.predict(['北 京 和 纽 约'.split()])[0],
            'B-City E-City O B-City E-City'.split())

    def test_simple_cn_nochar(self):
        tag = Tagger(batch_size=2, verbose=0, epochs=100, use_char=None)
        tag.fit(texts, labels)

        accuracy, recall, f1score = tag.score(texts, labels, detail=True)

        self.assertEqual(accuracy, 1.0)
        self.assertEqual(recall, 1.0)
        self.assertEqual(f1score, 1.0)

        self.assertEqual(tag.predict([texts[0]])[0], labels[0])

        self.assertEqual(
            tag.predict(['北 京 和 纽 约'.split()])[0],
            'B-City E-City O B-City E-City'.split())


if __name__ == '__main__':
    unittest.main()
