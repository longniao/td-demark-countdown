from strategy import Strategy
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
        for i in range(len(price_history) - pattern_size + 2):
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
        for i in range(len(price_history) - pattern_size + 2):
            print i
            if price_history[i]["close"] > price_history[i + 4]["close"] and \
                price_history[i+1]["close"] < price_history[i + 5]["close"]:
                print "here"
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

        pattern_size = 13
        for i in range(len(price_history) - pattern_size):
            # Starting from i, lookback 9 bars
            for j in range(9):
                if not price_history[i+j]["close"] > price_history[i+j+4]["close"]:
                    break
                if j == 8:
                    indices.append(i)
        self.cache["TD_SELL_SETUPS"] = {"indices": indices}
        return

            

    def td_buy_setup(self):
        """
        Returns list of indicies of the last_x TD Buy Setups

        :return list: Indicies of last_x TD Buy Setups
        """

        price_history = self.price_history
        indices = []

        pattern_size = 13
        for i in range(len(price_history) - pattern_size):
            # Starting from i, lookback 9 bars
            for j in range(9):
                if not price_history[i+j]["close"] < price_history[i+j+4]["close"]:
                    break
                if j == 8:
                    indices.append(i)
        self.cache["TD_BUY_SETUPS"] = {"indices": indices}
        return



