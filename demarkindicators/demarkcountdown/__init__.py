class DemarkCountdown():
    def __init__(self,price_history,open_key="open",close_key="close",high_key="high",low_key="low"):
        self.price_history = price_history
        self.cache = self._init_cache()
        self.keys = {}
        self.keys["high"] = high_key
        self.keys["low"] = low_key
        self.keys["open"] = open_key
        self.keys["close"] = close_key
    
    def _init_cache(self):
        cache = {}
        cache["LAST_BULLISH_PRICE_FLIP"] = None
        cache["LAST_BEARISH_PRICE_FLIP"] = None
        return cache
    
    def bearish_td_price_flip(self):
        """
        Return index of the last bearish price flip
        
        :return int: Index of price flip, -1 if none found
        """


        pass
    def bullish_td_price_flip(self):
        """
        Return index of the last bullish price flip
        
        :return int: Index of price flip, -1 if none found
        """


        pass