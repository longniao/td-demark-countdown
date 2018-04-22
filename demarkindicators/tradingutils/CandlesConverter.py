import json
class CandlesConverter():
    """
    Convert various candle formats to a standard format

    Standard Format:
        {
            "candles" : [
                {
                    "open":"",
                    "high":"",
                    "low":"",
                    "close:""
                }
            ]
        }
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
        standard_candle = {}
        for candle in candles["candles"]:
            standard_candle["open"] = float(candle["mid"]["o"])
            standard_candle["close"] = float(candle["mid"]["c"])
            standard_candle["high"] = float(candle["mid"]["h"])
            standard_candle["low"] = float(candle["mid"]["l"])
            standard_candles["candles"].append(standard_candle)
        # Reverse
        standard_candles["candles"] = standard_candles["candles"][::-1]
        return standard_candles