from strategy import Strategy
from tradingutils import CandleRanges
from pprint import pprint
import numpy as np
MAX_SEQUENTIAL_LOOKAHEAD = 5

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
        #    "active" : bool,
        #    "true_end_index", int,
        #    "true_range" : float,
        #    "true_high" : float,
        #    "true_low"  : float,
        #    "closing_range" : float,
        #    "max_high" : float,
        #    "min_low" : float,
        #    "max_close" : float,
        #    "min_close" : float
        # }
        
        cache["TD_SELL_SETUPS"] = [] 
        cache["TD_BUY_SETUPS"] = [] 
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
                        tdst_supports.append((CandleRanges.true_low(bar_nine_index + 8, price_history),bar_nine_index + 8))
        # If a pattern has been found
        if len(indices) > 0:
            self.cache["TDST_SUPPORT"] = (CandleRanges.true_low(indices[0]+8, price_history), indices[0]+8)

            for pattern_num in range(len(indices)):
                self.cache["TD_SELL_SETUPS"].append({
                    "index":indices[pattern_num], 
                    "perfect" : perfect_indicies[pattern_num],
                    "active" : None,
                    "tdst_support" : tdst_supports[pattern_num]
                    })
            
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
                        # TODO: Fix to be actual bar
                        tdst_resistances.append((CandleRanges.true_high(bar_nine_index + 8, price_history),bar_nine_index + 8))
                        
        if len(indices) > 0:
            self.cache["TDST_RESISTANCE"] = (CandleRanges.true_high(indices[0]+8, price_history),indices[0]+8) 

            for pattern_num in range(len(indices)):
                self.cache["TD_BUY_SETUPS"].append({
                        "index":indices[pattern_num], 
                        "perfect" : perfect_indicies[pattern_num],
                        "active" : True,
                        "tdst_resistance" : tdst_resistances[pattern_num]
                        })

            
        # Address Cancellation qualifier I
        # If 
        #   - Size of true range of most recent TD Buy Setup is equal to or greater than the size of the previous
        #       TD Buy Setup, but less than 1.618 times its size
        # Then
        #   - A TD Setup Recycle will occur, that is whicever TD Buy Setup has the larger true range will become the active 
        #       TD Buy Setup
        #
        # * Keeping in mind that the buy setup can extend beyond bar nine if there is no price flip to extinguish

        # Find the true indices and true ranges of all setups
        for x,pattern in enumerate(self.cache["TD_BUY_SETUPS"]):
            setup_index = pattern["index"]
            # Get true end of setup one
            true_end_setup = setup_index
            for i in range(1,setup_index+1):
                if price_history[setup_index-i]["close"] < price_history[setup_index-i+4]["close"] and \
                    setup_index-i not in self.cache['BULLISH_PRICE_FLIPS']['indices']:
                    true_end_setup -= 1
            true_range = CandleRanges.true_range(true_end_setup, setup_index+8, price_history)
            closing_range = CandleRanges.closing_range(true_end_setup, setup_index+8, price_history)
            price_extreme = CandleRanges.price_extreme(true_end_setup, setup_index+8, price_history)

            self.cache["TD_BUY_SETUPS"][x]["true_end_index"] = true_end_setup
            self.cache["TD_BUY_SETUPS"][x]["true_range"]     = true_range
            self.cache["TD_BUY_SETUPS"][x]["closing_range"]  = closing_range
            self.cache["TD_BUY_SETUPS"][x]["price_extreme"]  = price_extreme
            self.cache["TD_BUY_SETUPS"][x]["max_high"]       = CandleRanges.max_high(true_end_setup, setup_index+8, price_history)
            self.cache["TD_BUY_SETUPS"][x]["max_close"]      = CandleRanges.max_close(true_end_setup, setup_index+8, price_history)
            self.cache["TD_BUY_SETUPS"][x]["min_low"]        = CandleRanges.min_low(true_end_setup, setup_index+8, price_history)
            self.cache["TD_BUY_SETUPS"][x]["min_close"]      = CandleRanges.min_close(true_end_setup, setup_index+8, price_history)
            self.cache["TD_BUY_SETUPS"][x]["true_high"]      = CandleRanges.truest_high(true_end_setup, setup_index+8, price_history)
            self.cache["TD_BUY_SETUPS"][x]["true_low"]       = CandleRanges.truest_low(true_end_setup, setup_index+8, price_history)

        # Evaluate cancellation qualifier I, set active flag
        if len(self.cache["TD_BUY_SETUPS"]) >= 2:
            true_range_one = self.cache["TD_BUY_SETUPS"][0]["true_range"]
            true_range_two = self.cache["TD_BUY_SETUPS"][1]["true_range"]
            if true_range_one >= true_range_two and true_range_one <= 1.618 * true_range_two:
                print "[+] CQ I fulfilled"
                if true_range_one > true_range_two:
                    self.cache["TD_BUY_SETUPS"][0]["active"] = True
                    self.cache["TD_BUY_SETUPS"][1]["active"] = False
                if true_range_two > true_range_one:
                    self.cache["TD_BUY_SETUPS"][0]["active"] = False
                    self.cache["TD_BUY_SETUPS"][1]["active"] = True
        
        
        

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

    def td_buy_countdown(self,run_cancellation_qualifiers=True):
        price_history = self.price_history["candles"]
        indices = []

        # Run Cancellation Qualifier Check II & III
        if run_cancellation_qualifiers:
            self.td_buy_countdown_cancellation_qualifier_ii()
            self.td_buy_countdown_cancellation_qualifier_iii()

        # Iterate through current buy setups and their index in the cache
        for pattern_index, pattern in enumerate(self.cache["TD_BUY_SETUPS"]):
            # Do not evaluate pattern if it is not active (i.e. has not hit Cancellation Qualifier I)
            if not pattern["active"]:
                continue 
            

            setup_index = pattern["index"]
            true_range = CandleRanges.true_range(setup_index,setup_index + 8,price_history)
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
            countdown_bar_index = -1
            countdown_bars = [None] * 13

            # End at the most recent candle OR at the start of a later SELL setup at least 12 bars in the future
            end_index = setup_index
            for pattern in self.cache["TD_SELL_SETUPS"]:
                i = pattern["index"]
                if i < setup_index:
                    end_index = i
                    
            for x in range(0, end_index):
                countdown_bar_index = setup_index - x
                if countdown_bar_index in [pattern["index"] for pattern in self.cache["TD_SELL_SETUPS"]]:
                    # Countdown cancelled if there is a setup in the opposite direction
                    # pg 21
                    print "cancel 1"
                    break
                
                if CandleRanges.true_low(countdown_bar_index,price_history) > self.cache["TD_BUY_SETUPS"][pattern_index]["tdst_resistance"][0]: #self.cache["TD_BUY_SETUPS"]["tdst_resistance"][pattern_index][0]:
                    # Cancelled if the market trades higher and posts a true low above
                    # the true high of the prior TD Buy Setup (TDST Resistance)
                    # pg 21
                    print "cancel 2"
                    break

                if price_history[countdown_bar_index]["close"] <= price_history[countdown_bar_index + 2]["low"]:
                    if count < 13:
                        count +=1 
                        countdown_bars[count - 1] = price_history[countdown_bar_index]["close"]
                    #print "Count ",count," Close: ",price_history[countdown_bar_index]["close"]
                    
                    # Last bar
                    if count == 13 and price_history[countdown_bar_index]["low"] <= countdown_bars[7] and price_history[countdown_bar_index]["close"] <= price_history[countdown_bar_index + 2]["low"]:
                        countdown_bars[count - 1] = price_history[countdown_bar_index]["close"]
                        indices.append(countdown_bar_index)
            

        self.cache["TD_BUY_COUNTDOWNS"]["indices"] = indices

    def td_buy_countdown_cancellation_qualifier_ii(self):
        price_history = self.price_history["candles"]
        # Address cancellation qualifier II
        # If
        #   - The market has completed a TD Buy Setup that has a closing range within the true
        #       range of the prior TD Buy Setup, without recording a TD Sell Setup between the two
        # And
        #   - The current TD buy setup has a price extreme within the true range of the prior TD Buy Setup
        # Then
        #   - The prior TD Buy Setup  is the active TD Setup and the TD Buy Countdown relating to it remains intact
        # * Keeping in mind that the buy setup can extend beyond bar nine if there is no price flip to extinguish
        sandwich = False
        for pattern_number, pattern in enumerate(self.cache["TD_BUY_SETUPS"]):
            # Do not evaluate the last pattern
            if pattern_number == len(self.cache["TD_BUY_SETUPS"]) - 1:
                break

            prev_buy_setup = self.cache["TD_BUY_SETUPS"][pattern_number+1]

            # Check for sell patterns inbetween
            for sell_pattern in self.cache["TD_SELL_SETUPS"]:
                if sell_pattern["index"] > pattern["index"] and sell_pattern["index"] < prev_buy_setup["index"]:
                    sandwich = True
            if sandwich: 
                sandwich = False
                continue

            if (pattern["max_close"] <  prev_buy_setup["true_high"] and \
                pattern["min_close"] > prev_buy_setup["true_low"]):
                print "[+] Hit Cancellation Qualifier II"
                pattern["active"] = False

    def td_buy_countdown_cancellation_qualifier_iii(self):
        # Address cancellation qualifier III
        # If
        #   Setup is 18 bars or longer, do not do countdown
        for pattern in self.cache["TD_BUY_SETUPS"]:
            if (pattern["index"] - pattern["true_end_index"]) + 9 >= 18:
                print "[+] Hit Cancellation Qualifier III for pattern with index ",pattern["index"]
                pattern["active"] = False

