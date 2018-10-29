
"""
Performs various calculations
- true range
- true high
- true low

price_history is the spec in CandlesConverter
"""


# TODO: Sanity check index

class CandleRanges(object):
    def __init__(self):
        pass
    
    @staticmethod
    def true_low(index, price_history):
        return min(price_history[index]["low"],price_history[index+1]["close"])

    @staticmethod
    def true_high(index, price_history):
        return max(price_history[index]["high"],price_history[index+1]["close"])

    @classmethod
    def true_range(cls,low_index,high_index,price_history):
        """
        Since candles are most-recent in front, flip indices
        """
        truehigh = max([cls.true_high(i,price_history) for i in range(low_index,high_index+1)])
        truelow = min([cls.true_low(i,price_history) for i in range(low_index,high_index+1)])
        return truehigh - truelow

    @staticmethod
    def closing_range(low_index,high_index,price_history):
        closehigh = max([price_history[i]["close"] for i in range(low_index,high_index+1)])
        closelow = min([price_history[i]["close"] for i in range(low_index,high_index+1)])
        return closehigh - closelow

    @staticmethod
    def price_extreme(low_index,high_index,price_history):
        return max([price_history[i]["high"] for i in range(low_index,high_index+1)]) - \
                min([price_history[i]["low"] for i in range(low_index,high_index+1)])

    @staticmethod
    def min_low(low_index,high_index,price_history):
        return min([price_history[i]["low"] for i in range(low_index,high_index+1)])

    @staticmethod
    def max_high(low_index,high_index,price_history):
        return max([price_history[i]["high"] for i in range(low_index,high_index+1)])

    @staticmethod
    def min_close(low_index,high_index,price_history):
        return min([price_history[i]["close"] for i in range(low_index,high_index+1)])

    @staticmethod
    def max_close(low_index,high_index,price_history):
        return max([price_history[i]["close"] for i in range(low_index,high_index+1)])

    @classmethod
    def truest_high(cls,low_index,high_index,price_history):
        highest_high = cls.max_high(low_index,high_index,price_history)
        index = [price_history[i]["high"] for i in range(low_index,high_index+1)].index(highest_high)
        return cls.true_high(index,price_history[low_index:high_index+2])
    
    @classmethod
    def truest_low(cls,low_index,high_index,price_history):
        lowest_low = cls.min_low(low_index,high_index,price_history)
        index = [price_history[i]["low"] for i in range(low_index,high_index+1)].index(lowest_low)
        return cls.true_low(index,price_history[low_index:high_index+2])

    
    
    