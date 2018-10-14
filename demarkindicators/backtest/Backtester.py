from strategy import Strategy, Signal

class Backtester():
    """
        Simple backtester class
    """
    def __init__(self,Strategy,price_history,starting_account_balance = 10000):
        self.strategy = Strategy
        self.price_history = price_history
        self.account_balance = starting_account_balance
        self.open_order_cache = {}
        self.order_history_cache = {}

    def yieldCandle(self):
        candle =  self.price_history.pop()

        yield candle
    
    def openOrder(self,Signal):
        """
        openOrder:
            @param Signal: Signal parameter
            @return order_id: Unique order identifier

        Will open an order and keep in the order cache.
        Strategy object will pass Signals to the backtester.
        Signals must contain all information needed to open an order.

        """
        pass

    def closeOrder(self,order_identifier):
        """
        closeOrder:
            @param order_identifier: Order to close, format TBD
            @return bool: True if successful, throws error if not

            Strategy class contains and order closure logic. However,
            backtester will track for stoploss / takeprofit events.

            1. Fetch order from cache
            2. Mark as closed
            3. 
        """


        pass

    def setStopLoss(self):
        pass

    def setTakeProfit(self):
        pass

    def setOrderType(self):
        pass