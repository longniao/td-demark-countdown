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
        

        # Setup spec: 
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

        # Countdown spec:
        #   {
        #       "index" : int,
        #       "recycled" : bool,
        #       "setup_index" : int,
        #       "stop_loss" : float,
        #       "take_profit" : float,
        #       "bar_one_index" : int
        #   }
        cache["TD_SELL_COUNTDOWNS"] = []
        cache["TD_BUY_COUNTDOWNS"] = []

        # 9-13-9 spec:
        #   {
        #       "index" : int,
        #       "recycled" : bool,
        #       "countdown_index" : int,
        #       "stop_loss" : float,
        #       "take_profit" : float
        #   }
        cache["TD_BUY_9_13_9"] = []
        cache["TD_SELL_9_13_9"] = []

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
            if price_flip_index >= 8:
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
            if price_flip_index >= 8:
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
            for i in range(setup_index-1,0,-1):
                if price_history[i]["close"] < price_history[i+4]["close"]:
                    true_end_setup -= 1
                else:
                    break
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
        num_setups = len(self.cache["TD_BUY_SETUPS"])
        if num_setups >= 2:
            for i in range(num_setups-2,-1,-1):
                true_range_one = self.cache["TD_BUY_SETUPS"][i]["true_range"]
                true_range_two = self.cache["TD_BUY_SETUPS"][i+1]["true_range"]
                if true_range_one >= true_range_two and true_range_one <= 1.618 * true_range_two:
                    print "[+] CQ I fulfilled for BUY Setup with index ",self.cache["TD_BUY_SETUPS"][i]["index"]
                    if true_range_one > true_range_two:
                        self.cache["TD_BUY_SETUPS"][i]["active"] = True
                        self.cache["TD_BUY_SETUPS"][i+1]["active"] = False
                    if true_range_two > true_range_one:
                        self.cache["TD_BUY_SETUPS"][i]["active"] = False
                        self.cache["TD_BUY_SETUPS"][i+1]["active"] = True
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
        """
        td_buy_countdown:
            @param run_cancellation_qualifiers: bool 
        """
        price_history = self.price_history["candles"]
        countdowns = []

        # Run Cancellation Qualifier Check II & III
        if run_cancellation_qualifiers:
            self.td_buy_countdown_cancellation_qualifier_ii()
            self.td_buy_countdown_cancellation_qualifier_iiia()

        # Iterate through current buy setups and their index in the cache
        for pattern_index, pattern in enumerate(self.cache["TD_BUY_SETUPS"]):
            # Do not evaluate pattern if it is not active (i.e. has hit Cancellation Qualifier I)
            if not pattern["active"]:
                continue 
            

            setup_index = pattern["index"]
            # Don't analyze the setup if there have not been at least 12 bars
            # or if there is a sell setup index less than 12 bars away
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
            end_index = setup_index + 1
            for pattern in self.cache["TD_SELL_SETUPS"]:
                # TODO: Test
                i = pattern["index"]
                if i < setup_index:
                    end_index = i

            bar_one_index = -1 # For calculating stop loss
            for x in range(0, end_index):
                countdown_bar_index = setup_index - x 
                if countdown_bar_index in [pattern["index"] for pattern in self.cache["TD_SELL_SETUPS"]]:
                    # TODO: test
                    # Countdown cancelled if there is a setup in the opposite direction
                    # pg 21
                    print "cancel 1"
                    break
                
                if CandleRanges.true_low(countdown_bar_index,price_history) > self.cache["TD_BUY_SETUPS"][pattern_index]["tdst_resistance"][0]: #self.cache["TD_BUY_SETUPS"]["tdst_resistance"][pattern_index][0]:
                    # TODO: test
                    # Cancelled if the market trades higher and posts a true low above
                    # the true high of the prior TD Buy Setup (TDST Resistance)
                    # pg 21
                    print "cancel 2"
                    break

                if price_history[countdown_bar_index]["close"] <= price_history[countdown_bar_index + 2]["low"]:
                    if count < 12:
                        if count == 0:
                            bar_one_index = countdown_bar_index
                        count +=1 
                        
                        countdown_bars[count - 1] = price_history[countdown_bar_index]["close"]
                    # Last bar, remember count starts at 0
                    if count == 12 and price_history[countdown_bar_index]["low"] <= countdown_bars[7] and price_history[countdown_bar_index]["close"] <= price_history[countdown_bar_index + 2]["low"]:
                        countdown_bars[count - 1] = price_history[countdown_bar_index]["close"]

                        # Find the lowest low for the stop loss
                        lowest_low = price_history[countdown_bar_index]["low"]
                        lowest_low_index = countdown_bar_index
                        for x in range(countdown_bar_index, bar_one_index):
                            if price_history[x]["low"] < lowest_low:
                                lowest_low = CandleRanges.true_low(x,price_history)
                                lowest_low_index = x
                        
                        #TODO: test
                        stop_loss = lowest_low - (CandleRanges.true_high(lowest_low_index,price_history) - CandleRanges.true_low(lowest_low_index,price_history))
                        countdowns.append({ \
                            "index" : countdown_bar_index, \
                            "recycled" : False, \
                            "setup_index" : setup_index, \
                            "stop_loss" : stop_loss, \
                            "bar_one_index" : bar_one_index
                            })

                        break
            

        self.cache["TD_BUY_COUNTDOWNS"] = countdowns

    def td_buy_countdown_cancellation_qualifier_ii(self):
        #TODO: test
        """
        Address cancellation qualifier II
         If
           - The market has completed a TD Buy Setup that has a closing range within the true
               range of the prior TD Buy Setup, without recording a TD Sell Setup between the two
         And
           - The current TD buy setup has a price extreme within the true range of the prior TD Buy Setup
         Then
           - The prior TD Buy Setup  is the active TD Setup and the TD Buy Countdown relating to it remains intact
         * Keeping in mind that the buy setup can extend beyond bar nine if there is no price flip to extinguish
        """
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
                pattern["min_close"] > prev_buy_setup["true_low"]) and \
                (pattern["max_high"] < prev_buy_setup["true_high"] and \
                pattern["min_low"] > prev_buy_setup["true_low"]):
                print "[+] Hit Cancellation Qualifier II for pattern with index ",pattern["index"]
                pattern["active"] = False

    def td_buy_countdown_cancellation_qualifier_iiia(self):
        """
         Address cancellation qualifier III
         If
           Setup BEFORE countdown is 18 bars or longer, do not do countdown
        """
        for pattern in self.cache["TD_BUY_SETUPS"]:
            if (pattern["index"] - pattern["true_end_index"]) + 9 >= 18:
                print "[+] Hit Cancellation Qualifier IIIa for pattern with index ",pattern["index"]
                pattern["active"] = False

    def td_buy_countdown_cancellation_qualifier_iiib(self,countdown):
        #TODO: test
        """
        td_buy_countdown_cancellation_qualifier_iiib:
            @param coundown: Countdown object from the cache

        Address cancellation qualifier III
         If
           Setup AFTER or DURING countdown is 18 bars or longer, recycle
        """

        setup_index = countdown["setup_index"]

        # Find the next bullish price flip 
        closest_bullish_price_flip = filter(lambda x: x < setup_index, self.cache["BULLISH_PRICE_FLIPS"]["indices"])[-1]
        for pattern in self.cache["TD_BUY_SETUPS"]:
            if pattern["index"] > closest_bullish_price_flip and ((pattern["index"] - pattern["true_end_index"]) + 9 >= 18):
                    print "[+] Hit Cancellation Qualifier IIIb for pattern with index ",pattern["index"]
                    pattern["active"] = False
    
    def td_buy_9_13_9(self):
        #TODO: Test
        """
        td_buy_9_13_9:
        Conditions:
            1. The TD Buy Setup must not begin before or on the same price bar as the complete TD Buy Countdown
            2. The ensuing bullish TD Buy Setup mus tbe preceded by a TD Price Flip 
            3. No complete TD Sell Setup should occur prior to the appearance of the TD Buy Setup

        """
        price_history = self.price_history
        for countdown in self.cache["TD_BUY_COUNTDOWNS"]:
            for setup in self.cache["TD_BUY_SETUPS"]:
                # Only test first buy setup past countdown.
                if setup["index"] < countdown["index"]:
                    if len(filter(lambda x: x > setup["index"] + 8 and x < countdown["index"], self.cache["BULLISH_PRICE_FLIPS"])) == 1:
                    
                        sell_setups = [pattern["index"] for pattern in self.cache["TD_SELL_SETUPS"]]
                        if len(filter(lambda x: x > setup["index"] and x < countdown["index"], sell_setups)) == 0:
                            
                             
                            lowest_low = price_history[setup["index"]]["low"]
                            lowest_low_index = setup["index"]
                            for x in range(setup["index"],countdown["bar_one_index"]):
                                if price_history[x]["low"] < lowest_low:
                                    lowest_low = CandleRanges.true_low(x,price_history)
                                    lowest_low_index = x
                            
                            stop_loss = lowest_low - (CandleRanges.true_high(lowest_low_index,price_history) - CandleRanges.true_low(lowest_low_index,price_history))
                        
                            buy_9_13_9 = {
                                "index": setup["index"],
                                "countdown_index" : countdown["index"],
                                "stop_loss" : stop_loss
                            }

                            self.cache["TD_BUY_9_13_9"].append(buy_9_13_9)
                        else:
                            return
                    return
                    
        
