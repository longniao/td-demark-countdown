import unittest
from demarkcountdown import DemarkCountdown
from tradingutils import CandlesConverter
import json
import os
import sys
import logging
from pprint import pprint

curr_dir = os.path.dirname(os.path.realpath(__file__)) + "/"
candlesConverter = CandlesConverter()

class PriceFlipUnitTest(unittest.TestCase):
    def test_bullish_price_flip_single_pattern(self):
        candles = {}
        with open(curr_dir + "bullish_price_flip_and_sell_setup.json","r") as f:
            candles = json.loads(f.read())
        candles = candlesConverter.oanda(candles)
        
        demark = DemarkCountdown(candles)
        self.assertEquals(candles["candles"][0]["close"],56.312)

        demark.bullish_td_price_flip()
        cache = demark.cache
        self.assertEquals(cache["BULLISH_PRICE_FLIPS"]["indices"][0],9)

    def test_bullish_price_flip_double_pattern(self):
        pass
    def test_bearish_price_flip_single_pattern(self):
        pass

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
    def test_sell_setup_single_pattern(self):
        candles = {}
        with open(curr_dir + "bullish_price_flip_and_sell_setup.json","r") as f:
            candles = json.loads(f.read())
        candles = candlesConverter.oanda(candles)
        
        demark = DemarkCountdown(candles)
        self.assertEquals(candles["candles"][0]["close"],56.312)

        demark.td_sell_setup()
        cache = demark.cache
        self.assertEquals(cache["TD_SELL_SETUPS"]["indices"][0],0)
    def test_bearish_setup_double_pattern(self):
        pass
    def test_bearish_broken_setup(self):
        pass
    def test_bearish_perfect_setup(self):
        pass

if __name__ == "__main__":
    logging.basicConfig( stream=sys.stdout )
    logging.getLogger( "PriceFlipUnitTest.test_bearish_price_flip_single_pattern" ).setLevel( logging.DEBUG )
    unittest.main()