import unittest

from tma.analyst.kline import KlineAnalyst


class KlineAnalystTest(unittest.TestCase):
    def setUp(self):
        ts_code = '000001.SH'
        start = '20181101'
        freq = '60min'
        self.ts_code = ts_code
        self.k = KlineAnalyst(ts_code=ts_code, start=start,
                              freq=freq, cache_interval=0)

    def test_ma(self):
        self.k.ma_info()
        self.assertIn('close_ma5', self.k.kline.columns)
        self.assertIn('close_ma10', self.k.kline.columns)
        self.assertIn('close_ma20', self.k.kline.columns)

    def test_macd(self):
        self.k.macd_info()

    def test_simple(self):
        ka = KlineAnalyst(self.ts_code, freq='M', start='20000101',
                          source='pro', cache_interval=0)
        print(ka.kline.shape)


if __name__ == '__main__':
    unittest.main()

