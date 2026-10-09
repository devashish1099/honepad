class Simulation:
    def __init__(self):
        pass

    def place(self, timestamp, order_id, trader, side, price, qty):
        """Place a limit order. side is buy or sell. Returns the resting quantity, or None if the id was ever used or the input is invalid."""
        raise NotImplementedError

    def cancel(self, timestamp, order_id):
        """Remove a resting order. Returns its remaining quantity, or None."""
        raise NotImplementedError

    def get_order(self, timestamp, order_id):
        """Returns "side qty@price", such as "buy 5@100", or None."""
        raise NotImplementedError

    def trades(self, timestamp, n):
        """Last n trades, newest first, as buyId/sellId qty@price."""
        raise NotImplementedError

    def best(self, timestamp, side):
        """Best price on a side as price(totalQty), or None."""
        raise NotImplementedError

    def place_gtt(self, timestamp, order_id, trader, side, price, qty, ttl):
        """Like place, but the resting part expires at timestamp + ttl."""
        raise NotImplementedError

    def modify(self, timestamp, order_id, price, qty):
        """Change price and remaining quantity. Same price and no larger quantity keeps priority. Returns the remaining quantity, or None."""
        raise NotImplementedError

    def position(self, timestamp, trader):
        """Returns qty cash" for a trader, or None if unknown."""
        raise NotImplementedError

    def vwap(self, timestamp, start, end):
        """Integer VWAP of trades in [from, to), or None."""
        raise NotImplementedError

    def best_at(self, timestamp, side, time_at):
        """best as the book stood at timeAt."""
        raise NotImplementedError
