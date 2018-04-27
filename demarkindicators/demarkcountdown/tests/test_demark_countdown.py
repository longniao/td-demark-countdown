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
    def test_sell_setup_single_perfect_pattern(self):
        candles = {}
        with open(curr_dir + "bullish_price_flip_and_sell_setup.json","r") as f:
            candles = json.loads(f.read())
        candles = candlesConverter.oanda(candles)
        
        demark = DemarkCountdown(candles)
        self.assertEquals(candles["candles"][0]["close"],56.312)
        demark.bullish_td_price_flip()
        demark.td_sell_setup()
        cache = demark.cache
        self.assertEquals(cache["TD_SELL_SETUPS"]["indices"][0],1)
        self.assertEquals(cache["TD_SELL_SETUPS"]["perfect"][0],True)
        self.assertEquals(cache["TDST_SUPPORT"],(47.024, 9))
        self.assertEquals(demark.price_history["candles"][1]["close"],55.937)
    def test_sell_and_buy_setups(self):
        candles = {}
        with open(curr_dir + "sell_setup_and_buy_setup.json","r") as f:
            candles = json.loads(f.read())
        candles = candlesConverter.oanda(candles)
        
        demark = DemarkCountdown(candles)
        self.assertEquals(candles["candles"][0]["close"],63.774)
        demark.bullish_td_price_flip()
        demark.td_sell_setup()
        demark.bearish_td_price_flip()
        demark.td_buy_setup()
        cache = demark.cache
        pprint(cache)

        self.assertEquals(demark.price_history["candles"][cache["TD_SELL_SETUPS"]["indices"][0]]["close"],55.937)
        self.assertEquals(demark.price_history["candles"][cache["TD_BUY_SETUPS"]["indices"][0]]["close"],64.083)
        #self.assertEquals(True,False)
    def test_bearish_broken_setup(self):
        pass
    def test_perfect_sell_setup(self):
        pass

if __name__ == "__main__":
    logging.basicConfig( stream=sys.stdout )
    logging.getLogger( "PriceFlipUnitTest.test_bearish_price_flip_single_pattern" ).setLevel( logging.DEBUG )
    unittest.main()