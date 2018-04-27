from strategy import Strategy
from pprint import pprint
import numpy as np
MAX_SEQUENTIAL_LOOKAHEAD = 5

class DemarkCountdown():
    def __init__(self,price_history):
        self.price_history = price_history
        self.cache = self._init_cache()
    
    def _init_cache(self):
        cache = {}
        cache["BEARISH_PRICE_FLIPS"] = {}
        cache["BULLISH_PRICE_FLIPS"] = {}
        cache["TD_SELL_SETUPS"] = {}
        cache["TD_BUY_SETUPS"] = {}
        cache["TDST_SUPPORT"] = (None,None)
        cache["TDST_RESISTANCE"] = (None,None)
        return cache
    
    def bearish_td_price_flip(self):
        """
        Return list of the indicies of the most recent bearish price flip
        
        :param int last_x: How many price flips to return
        :return list: Indicies of last_x price flips
        """
        price_history = self.price_history["candles"]
        indices = []

        pattern_size = 6
        for i in range(len(price_history) - pattern_size + 1):
            if price_history[i]["close"] < price_history[i + 4]["close"] and \
                price_history[i+1]["close"] > price_history[i + 5]["close"]:
                indices.append(i)
        self.cache["BEARISH_PRICE_FLIPS"] = {"indices": indices}
        return


    def bullish_td_price_flip(self):
        """
        Return list of the indicies of the most recent bullish price flip
        
        :return list: Indicies of last_x price flips
        """
        price_history = self.price_history["candles"]
        indices = []

        pattern_size = 6
        for i in range(len(price_history) - pattern_size + 1):
            if price_history[i]["close"] > price_history[i + 4]["close"] and \
                price_history[i+1]["close"] < price_history[i + 5]["close"]:
                indices.append(i)
        self.cache["BULLISH_PRICE_FLIPS"] = {"indices": indices}
        return
    

    def td_sell_setup(self):
        """
        Returns list of indicies of the last_x TD Sell Setups

        :return list: Indicies of last_x TD Sell Setups
        """

        price_history = self.price_history["candles"]
        indices = []
        perfect_indicies = []

        # Must be preceded by bullish price flip
        bullish_td_price_flip_indices = self.cache["BULLISH_PRICE_FLIPS"]["indices"]
        for price_flip_index in bullish_td_price_flip_indices:
            if price_flip_index > 8:
                for j in range(9):
                    if not price_history[price_flip_index-j]["close"] > price_history[price_flip_index-j+4]["close"]:
                        break
                    if j == 8:
                        bar_nine_index = price_flip_index - j
                        indices.append(bar_nine_index)
                        perfect_indicies.append(self.perfect_td_sell_setup(bar_nine_index))
        
        most_recent_sell_setup = price_history[indices[0]:indices[0]+9]
        lows = [candle["low"] for candle in most_recent_sell_setup]
        low = min(lows)
        low_index = lows.index(low) + indices[0]
        self.cache["TDST_SUPPORT"] = (low, low_index)

        self.cache["TD_SELL_SETUPS"] = {"indices": indices, "perfect" : perfect_indicies}
        print pprint(self.cache)
        return

    def perfect_td_sell_setup(self,bar_nine_index):
        """
        Returns True if sell setup has been perfected

        :return bool: True if sell setup is perfect
        """
        price_history = self.price_history["candles"]
        if ( \
                (price_history[bar_nine_index]["close"] > price_history[bar_nine_index + 3]["close"] and price_history[bar_nine_index]["close"] > price_history[bar_nine_index + 2]["close"]) or \
                (price_history[bar_nine_index + 1]["close"] > price_history[bar_nine_index + 3]["close"] and price_history[bar_nine_index + 1]["close"] > price_history[bar_nine_index + 2]["close"]) or \
                self.delayed_sell_setup_perfection(bar_nine_index)
            ):
            return True
        return False

    def delayed_sell_setup_perfection(self,bar_nine_index):
        
        # Look five bars ahead MAX_SEQUENTIAL_LOOKAHEAD
        price_history = self.price_history["candles"]
        for index in range(1,MAX_SEQUENTIAL_LOOKAHEAD):
            if bar_nine_index - index < 0: # If index out of range
                return False
            if price_history[bar_nine_index - index]["close"] > price_history[bar_nine_index + 3]["close"] and \
                price_history[bar_nine_index - index]["close"] > price_history[bar_nine_index + 2]["close"]:
                return True
        return False


    def td_buy_setup(self):
        """
        Returns list of indicies of the last_x TD Buy Setups

        :return list: Indicies of last_x TD Buy Setups
        """

        price_history = self.price_history["candles"]
        indices = []
        perfect_indicies = []

        # Must be preceded by bearish price flip
        bearish_td_price_flip_indices = self.cache["BEARISH_PRICE_FLIPS"]["indices"]
        for price_flip_index in bearish_td_price_flip_indices:
            if price_flip_index > 8:
                for j in range(9):
                    if not price_history[price_flip_index-j]["close"] < price_history[price_flip_index-j+4]["close"]:
                        break
                    if j == 8:
                        bar_nine_index = price_flip_index - j
                        indices.append(bar_nine_index)
                        perfect_indicies.append(self.perfect_td_buy_setup(bar_nine_index))
        
        most_recent_buy_setup = price_history[indices[0]:indices[0]+9]
        highs = [candle["high"] for candle in most_recent_buy_setup]
        high = max(highs)
        high_index = highs.index(high) + indices[0]
        self.cache["TDST_RESISTANCE"] = (high, high_index)

        self.cache["TD_BUY_SETUPS"] = {"indices": indices, "perfect" : perfect_indicies}
        print pprint(self.cache)
        return

    def perfect_td_buy_setup(self,bar_nine_index):
        """
        Returns True if sell setup has been perfected

        :return bool: True if sell setup is perfect
        """
        price_history = self.price_history["candles"]
        if ( \
                (price_history[bar_nine_index]["close"] < price_history[bar_nine_index + 3]["close"] and price_history[bar_nine_index]["close"] < price_history[bar_nine_index + 2]["close"]) or \
                (price_history[bar_nine_index + 1]["close"] < price_history[bar_nine_index + 3]["close"] and price_history[bar_nine_index + 1]["close"] < price_history[bar_nine_index + 2]["close"]) or \
                self.delayed_buy_setup_perfection(bar_nine_index)
            ):
            return True
        return False

    def delayed_buy_setup_perfection(self,bar_nine_index):
        
        # Look five bars ahead MAX_SEQUENTIAL_LOOKAHEAD
        price_history = self.price_history["candles"]
        for index in range(1,MAX_SEQUENTIAL_LOOKAHEAD):
            if bar_nine_index - index < 0: # If index out of range
                return False
            if price_history[bar_nine_index - index]["close"] < price_history[bar_nine_index + 3]["close"] and \
                price_history[bar_nine_index - index]["close"] < price_history[bar_nine_index + 2]["close"]:
                return True
        return False



