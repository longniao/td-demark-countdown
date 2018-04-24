from tradingutils import CandlesConverter
import unittest
import json
import os
import sys
import logging

curr_dir = os.path.dirname(os.path.realpath(__file__)) + "/"
candlesConverter = CandlesConverter()

class CandlesConverterTests(unittest.TestCase):
    def oanda_test(self):
        candles = {}
        log = logging.getLogger( "CandlesConverterTests.oanda_test" )
        with open(curr_dir + "oanda.json","r") as f:
            candles = json.loads(f.read())
        
        log.debug(candles)
        candles = candlesConverter.oanda(candles)
        log.debug(candles)
        self.assertEqual(candles["candles"][0]["open"],1.09954)
        self.assertEqual(candles["candles"][1]["open"],1.09951)

if __name__ == "__main__":
    logging.basicConfig( stream=sys.stdout )
    logging.getLogger( "CandlesConverterTests.oanda_test" ).setLevel( logging.DEBUG )
    unittest.main()