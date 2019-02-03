import unittest

from torch_tagger import Tagger


class TestScoreTable(unittest.TestCase):
    def test_simple_cn(self):
        texts = [
            '我 今 天 想 飞 到 纽 约',
            '定 个 酒 店 在 东 京',
            '北 京 现 在 什 么 时 间 ?',
        ]
        labels = [
            'O B-Date E-Date O O O B-City E-City',
            'O O O O O B-City E-City',
            'B-City E-City O O O O O O O',
        ]

        texts = [x.split() for x in texts]
        labels = [x.split() for x in labels]

        tag = Tagger(batch_size=2, verbose=0, epochs=50)
        tag.fit(texts, labels)

        table = tag.score_table(texts, labels)
        print(table)
        self.assertEqual(len(table), 3)


if __name__ == '__main__':
    unittest.main()
