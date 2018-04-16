import Strategy
class DemarkCountdown(Strategy):
    def __init__(self,open_key="open",close_key="close",high_key="high",low_key="low"):
        self.cache = self._init_cache()
        self.keys = {}
        self.keys["high"] = high_key
        self.keys["low"] = low_key
        self.keys["open"] = open_key
        self.keys["close"] = close_key
    
    def _init_cache(self):
        cache = {}
        cache["LAST_BEARISH_PRICE_FLIPS"] = []
        cache["LAST_BULLISH_PRICE_FLIPS"] = []
        cache["LAST_TD_SELL_SETUPS"] = []
        cache["LAST_TD_BUY_SETUPS"] = []
        return cache
    
    def bearish_td_price_flip(self,last_x=1):
        """
        Return list of the indicies of the most recent bearish price flip
        
        :param int last_x: How many price flips to return
        :return list: Indicies of last_x price flips, [-1] if none found
        """
        keys = self.keys
        price_history = self.price_history
        indicies = []

        pattern_size = 6
        for i in range(len(price_history) - pattern_size):
            if price_history[i][keys["close"]] < price_history[i + 4][keys["close"]] and \
                price_history[i+1][keys["close"]] > price_history[i + 5][keys["close"]]:
                indicies.append(i)
            if len(indicies) == last_x:
                self.cache["LAST_BEARISH_PRICE_FLIPS"] = indicies
                return
        self.cache["LAST_BEARISH_PRICE_FLIP"] = [-1]
        return


    def bullish_td_price_flip(self,last_x=1):
        """
        Return list of the indicies of the most recent bullish price flip
        
        :param int last_x: How many price flips to return
        :return list: Indicies of last_x price flips, [-1] if none found
        """
        keys = self.keys
        price_history = self.price_history
        indicies = []


        pattern_size = 6
        for i in range(len(price_history) - pattern_size):
            if price_history[i][keys["close"]] > price_history[i + 4][keys["close"]] and \
                price_history[i+1][keys["close"]] < price_history[i + 5][keys["close"]]:
                indicies.append(i)
            if len(indicies) == last_x:
                self.cache["LAST_BULLISH_PRICE_FLIPS"] = indicies
                return
        self.cache["LAST_BULLISH_PRICE_FLIP"] = [-1]
        return
    

    def td_sell_setup(self, last_x=2):
        """
        Returns list of indicies of the last_x TD Sell Setups

        :param int last_x: How many indicies of buy setups to return
        :return list: Indicies of last_x TD Sell Setups
        """

        keys = self.keys
        price_history = self.price_history
        indicies = []

        pattern_size = 13
        for i in range(len(price_history) - pattern_size):
            # Starting from i, lookback 9 bars
            for j in range(9):
                if not price_history[i+j][keys["close"]] > price_history[i+j+4][keys["close"]]:
                    break
                if j == 8:
                    indicies.append(i)
                    if len(indicies) == last_x:
                        self.cache["LAST_TD_SELL_SETUPS"] = indicies
                        return
        self.cache["LAST_TD_SELL_SETUPS"] = [-1]
        return

            

    def td_buy_setup(self, last_x=2):
        """
        Returns list of indicies of the last_x TD Buy Setups

        :param int last_x: How many indicies of buy setups to return
        :return list: Indicies of last_x TD Buy Setups
        """

        keys = self.keys
        price_history = self.price_history

        indicies = []

        pattern_size = 13
        for i in range(len(price_history) - pattern_size):
            # Starting from i, lookback 9 bars
            for j in range(9):
                if not price_history[i+j][keys["close"]] < price_history[i+j+4][keys["close"]]:
                    break
                if j == 8:
                    indicies.append(i)
                    if len(indicies) == last_x:
                        self.cache["LAST_TD_SELL_SETUPS"] = indicies
                        return
        self.cache["LAST_TD_SELL_SETUPS"] = [-1]
        return



