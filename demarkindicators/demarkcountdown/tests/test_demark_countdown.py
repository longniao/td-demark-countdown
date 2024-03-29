import unittest
from demarkcountdown import DemarkCountdown
from tradingutils import CandlesConverter, CandleRanges
import json
import os
import sys
import logging
from pprint import pprint

curr_dir = os.path.dirname(os.path.realpath(__file__)) + "/"
candlesConverter = CandlesConverter()

# TODO: Tests for closing range, price extreme
class TrueRangeHighLowTest(unittest.TestCase):
    def test_true_low(self):
        candles = {}
        with open(curr_dir + "TrueRangeHighLowCandles/true_low.json","r") as f:
            candles = json.loads(f.read())
        candles = candlesConverter.oanda(candles)
        self.assertEquals(CandleRanges.true_low(0,candles["candles"]), 9.78)
        self.assertEquals(CandleRanges.true_low(2,candles["candles"]), 9.85)

        with open(curr_dir + "TrueRangeHighLowCandles/true_low_is_close.json","r") as f:
            candles = json.loads(f.read())
        candles = candlesConverter.oanda(candles)
        self.assertEquals(CandleRanges.true_low(0,candles["candles"]), 1.07246)

    def test_true_high(self):
        candles = {}
        with open(curr_dir + "TrueRangeHighLowCandles/true_high.json","r") as f:
            candles = json.loads(f.read())
        candles = candlesConverter.oanda(candles)
        self.assertEquals(CandleRanges.true_high(0,candles["candles"]), 13.22)
        self.assertEquals(CandleRanges.true_high(2,candles["candles"]), 13.36)
    def test_true_range(self):
        candles = {}
        with open(curr_dir + "TrueRangeHighLowCandles/true_range_buy_setup.json","r") as f:
            candles = json.loads(f.read())
        candles = candlesConverter.oanda(candles)
        demark = DemarkCountdown(candles)
        demark.bullish_td_price_flip()
        demark.bearish_td_price_flip()
        demark.td_buy_setup()

        first_buy_setup = demark.cache["TD_BUY_SETUPS"][0]["index"]
        self.assertEquals(first_buy_setup,1)

        # Float likely to be a little off
        self.assertAlmostEquals(CandleRanges.true_range(first_buy_setup,first_buy_setup+8,candles["candles"]),.00000074)

class PriceFlipUnitTest(unittest.TestCase):
    def test_bullish_price_flip_single_pattern(self):
        candles = {}
        with open(curr_dir + "bullish_price_flip_and_sell_setup.json","r") as f:
            candles = json.loads(f.read())
        candles = candlesConverter.oanda(candles)
        
        demark = DemarkCountdown(candles)
        # Test candles successfully converted
        self.assertEquals(candles["candles"][0]["close"],56.312)

        # Confirm price flip
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
        # Test candles successfully converted
        self.assertEquals(candles["candles"][0]["close"],56.312)
        demark.bullish_td_price_flip()
        demark.td_sell_setup()
        cache = demark.cache

        self.assertEquals(cache["TD_SELL_SETUPS"][0]["index"],1)
        self.assertEquals(cache["TD_SELL_SETUPS"][0]["perfect"],True)
        self.assertEquals(cache["TD_SELL_SETUPS"][0]["tdst_support"],(47.024, 9))

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
        demark.bearish_td_price_flip()
        demark.td_sell_setup()
        demark.td_buy_setup()
        cache = demark.cache
        pprint(cache)

        self.assertEquals(demark.price_history["candles"][cache["TD_SELL_SETUPS"][0]["index"]]["close"],55.937)
        self.assertEquals(demark.price_history["candles"][cache["TD_BUY_SETUPS"][0]["index"]]["close"],64.083)

        self.assertEquals(demark.cache["TDST_RESISTANCE"],(74.164,9))
        self.assertEquals(demark.cache["TDST_SUPPORT"],(47.024,33))
        #self.assertEquals(True,False)
    def test_bearish_broken_setup(self):
        pass
    def test_perfect_sell_setup(self):
        pass

class TDCountdownUnitTest(unittest.TestCase):
    def test_buy_setup_and_demark_countdown_pattern(self):
        """
        candles = {}
        with open(curr_dir + "Countdowns/bullish_demark_countdown_two.json","r") as f:
            candles = json.loads(f.read())

        candles = candlesConverter.oanda(candles)
        demark = DemarkCountdown(candles)
        demark.bullish_td_price_flip()
        demark.bearish_td_price_flip()
        demark.td_sell_setup()
        demark.td_buy_setup()
        demark.td_buy_countdown(run_cancellation_qualifiers=False)
        cache = demark.cache
        #pprint(cache)
        self.assertEquals(cache["TD_BUY_COUNTDOWNS"][0]['index'],2)

        with open(curr_dir + "Countdowns/bullish_demark_countdown_one.json","r") as f:
            candles = json.loads(f.read())
        candles = candlesConverter.oanda(candles)
        demark = DemarkCountdown(candles)
        demark.bullish_td_price_flip()
        demark.bearish_td_price_flip()
        demark.td_sell_setup()
        demark.td_buy_setup()
        demark.td_buy_countdown(run_cancellation_qualifiers=True)
        cache = demark.cache
        pprint(cache)
        self.assertEquals(cache["TD_BUY_COUNTDOWNS"][0]['index'],1)
        """
        pass
    def test_buy_countdown_end_index(self):
        pass
class TDCancellationQualifiersUnitTest(unittest.TestCase):
    def test_buy_countdown_cancellation_qualifier_i(self):
        candles = {}
        with open(curr_dir + "CancellationQualifiers/CancellationQualifierI/two_bullish_setups_cq1.json","r") as f:
            candles = json.loads(f.read())

        candles = candlesConverter.oanda(candles)
        demark = DemarkCountdown(candles)
        demark.bullish_td_price_flip()
        demark.bearish_td_price_flip()
        demark.td_sell_setup()
        demark.td_buy_setup()
        demark.td_buy_countdown(run_cancellation_qualifiers=True)
        cache = demark.cache
        pprint(cache)
        self.assertGreaterEqual(cache['TD_BUY_SETUPS'][0]["true_range"],cache['TD_BUY_SETUPS'][1]["true_range"])
        self.assertLessEqual(cache['TD_BUY_SETUPS'][0]["true_range"], 1.618 * cache['TD_BUY_SETUPS'][1]["true_range"])
        self.assertEquals(cache['TD_BUY_SETUPS'][0]["active"],True)
        self.assertEquals(cache['TD_BUY_SETUPS'][1]["active"],False)
    def test_buy_countdown_cancellation_qualifier_ii(self):
        candles = {}
        with open(curr_dir + "CancellationQualifiers/CancellationQualifierII/buy_setup_cancellation_qualifier_ii.json","r") as f:
            candles = json.loads(f.read())

        candles = candlesConverter.oanda(candles)
        demark = DemarkCountdown(candles)
        demark.bullish_td_price_flip()
        demark.bearish_td_price_flip()
        #demark.td_sell_setup() # Ignore the sell setup so CCII can be tested 
        demark.td_buy_setup()
        demark.td_buy_countdown(run_cancellation_qualifiers=True)
        cache = demark.cache
        pprint(cache)

        self.assertEquals(cache['TD_BUY_SETUPS'][0]['active'],False)
    def test_buy_countdown_recycle_iii(self):
        pass
        """
        candles = {}
        with open(curr_dir + "CancellationQualifiers/CancellationQualifierIII/three_buy_countdowns_and_recycle.json","r") as f:
            candles = json.loads(f.read())

        candles = candlesConverter.oanda(candles)
        demark = DemarkCountdown(candles)
        demark.bullish_td_price_flip()
        demark.bearish_td_price_flip()
        demark.td_sell_setup()
        demark.td_buy_setup()
        demark.td_buy_countdown(run_cancellation_qualifiers=True)
        cache = demark.cache
        pprint(cache)

        self.assertEquals(cache['TD_BUY_COUNTDOWNS'][0]['index'],4)
        self.assertEquals(cache['TD_BUY_COUNTDOWNS'][0]['setup_index'],25)
        self.assertAlmostEquals(cache['TD_BUY_SETUPS'][-1]['true_end_index'],20)
        self.assertEqual(False,True)
        """
    def test_buy_countdown_recycle_iiia(self):
        pass
    def test_buy_countdown_recycle_iiib(self):
        pass
    
if __name__ == "__main__":
    logging.basicConfig( stream=sys.stdout )
    logging.getLogger( "PriceFlipUnitTest.test_bearish_price_flip_single_pattern" ).setLevel( logging.DEBUG )
    unittest.main()