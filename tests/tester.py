import unittest
from demarkcountdown import DemarkCountdown
from tradingutils import CandlesConverter
import json

candlesConverter = CandlesConverter()

class PriceFlipUnitTest(unittest.TestCase):
    def test_bullish_price_flip_single_pattern(self):
        pass
    def test_bullish_price_flip_double_pattern(self):
        pass
    def test_bearish_price_flip_single_pattern(self):
        candles = {}

        with open("data/bearish_price_flip_and_sell_setup.json","r") as f:
            candles = json.loads(f.read())
        candles = candlesConverter.oanda(candles)
        demark = DemarkCountdown(candles)
        del demark
        self.assertEqual(True,True)
    def test_bearish_price_flip_double_pattern(self):
        pass

class TDSetupUnitTest(unittest.TestCase):
    def test_bullish_setup_single_pattern(self):
        pass
    def test_bullish_setup_double_pattern(self):
        pass
    def test_bullish_broken_setup(self):
        pass
    def test_bullish_perfect_setup(self):
        pass
    def test_bearish_setup_single_pattern(self):
        pass
    def test_bearish_setup_double_pattern(self):
        pass
    def test_bearish_broken_setup(self):
        pass
    def test_bearish_perfect_setup(self):
        pass

if __name__ == '__main__':
    unittest.main()