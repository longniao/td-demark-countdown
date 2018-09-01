import json
from pprint import pprint
class CandlesConverter():
    """
    Convert various candle formats to a standard format

    Standard Format:
        {
            "candles" : [
                {
                    "open":float,
                    "high":float,
                    "low":float,
                    "close:float
                }
            ]
        }

    This format will have the most recent candle at index 0
    """
    def __init__(self):
        pass
    def _standard_candles_dict(self):
        """
        Return a standard candles object
        """
        standard_candles = {}
        standard_candles["candles"] = []
        return standard_candles

    def oanda(self,candles):
        """
        Convert object from Oanda style candles object into standard object
        """
        standard_candles = self._standard_candles_dict()
        standard_candles["candles"] = [None] * len(candles["candles"])
        for index,candle in enumerate(candles["candles"]):
            standard_candles["candles"][index] = {}
            standard_candles["candles"][index]["open"] = float(candle["mid"]["o"])
            standard_candles["candles"][index]["close"] = float(candle["mid"]["c"])
            standard_candles["candles"][index]["high"] = float(candle["mid"]["h"])
            standard_candles["candles"][index]["low"] = float(candle["mid"]["l"])
        # Reverse
        pprint(standard_candles)
        standard_candles["candles"] = standard_candles["candles"][::-1]
        return standard_candles