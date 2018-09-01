from strategy import Strategy
from pprint import pprint
import numpy as np
MAX_SEQUENTIAL_LOOKAHEAD = 5


# TODO: Go back through setups and flips to make sure true lows / true highs are correctly calculated
#

true_low = lambda index,price_history: min(price_history[index]["low"],price_history[index+1]["close"])
true_high = lambda index,price_history: max(price_history[index]["high"],price_history[index+1]["close"])

def setup_true_range(bar_one_index, bar_nine_index, price_history):
    truehigh = max([true_high(i,price_history) for i in range(bar_nine_index,bar_one_index)])
    truelow = min([true_low(i,price_history) for i in range(bar_nine_index,bar_one_index)])
    return truehigh - truelow
    

class DemarkCountdown():
    def __init__(self,price_history):
        self.price_history = price_history
        self.cache = self._init_cache()
    
    def _init_cache(self):
        cache = {}
        cache["BEARISH_PRICE_FLIPS"] = {"indices": []}
        cache["BULLISH_PRICE_FLIPS"] = {"indices": []}
        

        # spec: 
        # {
        #    "index" : int,
        #    "tdst_support/tdst_resistance" : (float,int),
        #    "perfect" : bool,
        #    "active" : bool
        # }
        
        cache["TD_SELL_SETUPS"] = [] # {"indices": [], "perfect" : [], "tdst_support": []}
        cache["TD_BUY_SETUPS"] = [] #{"indices": [], "perfect" : [], "tdst_resistance": []}
        cache["TD_SELL_COUNTDOWNS"] = {}
        cache["TD_BUY_COUNTDOWNS"] = {}
        # Level + bar number, this is the latest
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
        tdst_supports = []

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
                        tdst_supports.append((true_low(bar_nine_index + 8, price_history),bar_nine_index + 8))
        # If a pattern has been found
        if len(indices) > 0:
            self.cache["TDST_SUPPORT"] = (true_low(indices[0]+8, price_history), indices[0]+8)

            for pattern_num in range(len(indices)):
                self.cache["TD_SELL_SETUPS"].append({
                    "index":indices[pattern_num], 
                    "perfect" : perfect_indicies[pattern_num],
                    "active" : None,
                    "tdst_support" : tdst_supports[pattern_num]
                    })
            #self.cache["TD_SELL_SETUPS"] = {"indices": indices, "perfect" : perfect_indicies, "tdst_support": tdst_supports}
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
        tdst_resistances = []

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
                        tdst_resistances.append((true_high(bar_nine_index + 8, price_history),bar_nine_index + 8))
                        
        if len(indices) > 0:
            self.cache["TDST_RESISTANCE"] = (true_high(indices[0]+8, price_history),indices[0]+8) 

            for pattern_num in range(len(indices)):
                self.cache["TD_BUY_SETUPS"].append({
                        "index":indices[pattern_num], 
                        "perfect" : perfect_indicies[pattern_num],
                        "active" : None,
                        "tdst_resistance" : tdst_resistances[pattern_num]
                        })

            #self.cache["TD_BUY_SETUPS"] = {"indices": indices, "perfect" : perfect_indicies, "tdst_resistance" : tdst_resistances}
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

    def td_buy_countdown(self):
        price_history = self.price_history["candles"]
        indices = []

        # Iterate through current buy setups and their index in the cache
        for pattern_index, pattern in enumerate(self.cache["TD_BUY_SETUPS"]):
            setup_index = pattern["index"]
            true_range = setup_true_range(setup_index + 8,setup_index,price_history)
            print "True Range: ",true_range
            # Don't analyze the setup if there have not been at least 12 bars
            # or if there is a sell setup index less than 12 bars away
            print "Setup: ",price_history[setup_index]
            if setup_index < 13: 
                continue
            for pattern in range(len(self.cache["TD_SELL_SETUPS"])):
                i = pattern["index"]
                if setup_index > i and i > setup_index - 12:
                    continue

            print "Setup price: ",price_history[setup_index]
            count = 0
            current_index = -1
            countdown_bar_index = -1
            countdown_bars = [None] * 13
            # Start the countdown if the close of the last bar of the buy setup is less than the close
            # two bars earlier
            if count == 0 and price_history[setup_index]["close"] <= price_history[setup_index-2]["low"]:
                print "here ",price_history[setup_index]["close"], price_history[setup_index + 2]["low"]
                    
                count = 1
                current_index = setup_index
                countdown_bars[count - 1] = price_history[setup_index]["close"]
                countdown_bar_index = setup_index

            # End at the most recent candle OR at the start of a later SELL setup at least 12 bars in the future
            end_index = len(price_history)
            for pattern in self.cache["TD_SELL_SETUPS"]:
                i = pattern["index"]
                if i < setup_index:
                    end_index = i

            for x in range(1, end_index - setup_index):
                

                print "Count: ",count," countdown_bar_index: ",countdown_bar_index
                if countdown_bar_index in [pattern["index"] for pattern in self.cache["TD_SELL_SETUPS"]]:
                    # Countdown cancelled if there is a setup in the opposite direction
                    # pg 21
                    print "cancel 1"
                    break
                
                if true_low(countdown_bar_index,price_history) > self.cache["TD_BUY_SETUPS"][pattern_index]["tdst_resistance"][0]: #self.cache["TD_BUY_SETUPS"]["tdst_resistance"][pattern_index][0]:
                    # Cancelled if the market trades higher and posts a true low above
                    # the true high of the prior TD Buy Setup (TDST Resistance)
                    # pg 21
                    print "cancel 2"
                    break

                if price_history[countdown_bar_index]["close"] <= price_history[countdown_bar_index + 2]["low"]:
                    if count < 13:
                        count +=1 
                        countdown_bars[count - 1] = price_history[countdown_bar_index]["close"]
                    print "Count ",count," Close: ",price_history[countdown_bar_index]["close"]
                    
                    # Last bar
                    if count == 13 and price_history[countdown_bar_index]["low"] <= countdown_bars[7] and price_history[countdown_bar_index]["close"] <= price_history[countdown_bar_index + 2]["low"]:
                        count = count + 1
                        countdown_bars[count - 1] = price_history[countdown_bar_index]["close"]
                        indices.append(countdown_bar_index)
            
                # Move from setup bar 9 towards the latest bar
                countdown_bar_index = setup_index - x

        self.cache["TD_BUY_COUNTDOWNS"]["indices"] = indices



