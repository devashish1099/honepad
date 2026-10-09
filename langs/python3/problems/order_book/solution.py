class Simulation:
    def __init__(self):
        # order_id -> [trader, side, price, remaining, seq, expiry]
        self.resting = {}
        self.used_ids = set()
        self.seq = 0
        self.trade_log = []
        self.traders = {}
        self.snapshots = []

    # bookkeeping

    def _expire(self, timestamp):
        for order_id in [o for o, r in self.resting.items() if r[5] is not None]:
            if timestamp >= self.resting[order_id][5]:
                del self.resting[order_id]

    def _snapshot(self, timestamp):
        rows = [(r[1], r[2], r[3], r[5]) for r in self.resting.values()]
        if self.snapshots and self.snapshots[-1][0] == timestamp:
            self.snapshots[-1] = (timestamp, rows)
        else:
            self.snapshots.append((timestamp, rows))

    def _next_seq(self):
        self.seq += 1
        return self.seq

    def _match(self, timestamp, order_id):
        trader, side, price, remaining, _seq, _exp = self.resting[order_id]
        opposite = "sell" if side == "buy" else "buy"
        while remaining > 0:
            best = None
            for other_id, row in self.resting.items():
                if row[1] != opposite:
                    continue
                if side == "buy" and row[2] > price:
                    continue
                if side == "sell" and row[2] < price:
                    continue
                key = (row[2] if side == "buy" else -row[2], row[4])
                if best is None or key < best[0]:
                    best = (key, other_id)
            if best is None:
                break
            other_id = best[1]
            other = self.resting[other_id]
            qty = min(remaining, other[3])
            trade_price = other[2]
            remaining -= qty
            other[3] -= qty
            buy_id, sell_id = (order_id, other_id) if side == "buy" else (other_id, order_id)
            buyer = trader if side == "buy" else other[0]
            seller = other[0] if side == "buy" else trader
            self.trade_log.append((timestamp, buy_id, sell_id, qty, trade_price))
            self.traders[buyer][0] += qty
            self.traders[buyer][1] -= qty * trade_price
            self.traders[seller][0] -= qty
            self.traders[seller][1] += qty * trade_price
            if other[3] == 0:
                del self.resting[other_id]
        if remaining == 0:
            del self.resting[order_id]
        else:
            self.resting[order_id][3] = remaining
        return remaining

    def _place(self, timestamp, order_id, trader, side, price, qty, expiry):
        self._expire(timestamp)
        if order_id in self.used_ids or side not in ("buy", "sell") or qty <= 0 or price <= 0:
            self._snapshot(timestamp)
            return None
        self.used_ids.add(order_id)
        self.traders.setdefault(trader, [0, 0])
        self.resting[order_id] = [trader, side, price, qty, self._next_seq(), expiry]
        left = self._match(timestamp, order_id)
        self._snapshot(timestamp)
        return left

    # level 1

    def place(self, timestamp, order_id, trader, side, price, qty):
        return self._place(timestamp, order_id, trader, side, price, qty, None)

    def cancel(self, timestamp, order_id):
        self._expire(timestamp)
        row = self.resting.pop(order_id, None)
        self._snapshot(timestamp)
        return None if row is None else row[3]

    def get_order(self, timestamp, order_id):
        self._expire(timestamp)
        self._snapshot(timestamp)
        row = self.resting.get(order_id)
        if row is None:
            return None
        return f"{row[1]} {row[3]}@{row[2]}"

    # level 2

    def trades(self, timestamp, n):
        self._expire(timestamp)
        self._snapshot(timestamp)
        recent = self.trade_log[::-1][:n]
        return [f"{b}/{s} {q}@{p}" for _t, b, s, q, p in recent]

    def best(self, timestamp, side):
        self._expire(timestamp)
        self._snapshot(timestamp)
        return _best_level([(r[1], r[2], r[3], r[5]) for r in self.resting.values()], side)

    # level 3

    def place_gtt(self, timestamp, order_id, trader, side, price, qty, ttl):
        if ttl <= 0:
            self._expire(timestamp)
            self._snapshot(timestamp)
            return None
        return self._place(timestamp, order_id, trader, side, price, qty, timestamp + ttl)

    def modify(self, timestamp, order_id, price, qty):
        self._expire(timestamp)
        row = self.resting.get(order_id)
        if row is None or qty <= 0 or price <= 0:
            self._snapshot(timestamp)
            return None
        if price == row[2] and qty <= row[3]:
            row[3] = qty
            self._snapshot(timestamp)
            return qty
        row[2] = price
        row[3] = qty
        row[4] = self._next_seq()
        left = self._match(timestamp, order_id)
        self._snapshot(timestamp)
        return left

    # level 4

    def position(self, timestamp, trader):
        self._expire(timestamp)
        self._snapshot(timestamp)
        row = self.traders.get(trader)
        if row is None:
            return None
        return f"{row[0]} {row[1]}"

    def vwap(self, timestamp, start, end):
        self._expire(timestamp)
        self._snapshot(timestamp)
        rows = [(q, p) for t, _b, _s, q, p in self.trade_log if start <= t < end]
        volume = sum(q for q, _p in rows)
        if volume == 0:
            return None
        return sum(q * p for q, p in rows) // volume

    def best_at(self, timestamp, side, time_at):
        self._expire(timestamp)
        self._snapshot(timestamp)
        chosen = None
        for when, rows in self.snapshots:
            if when <= time_at:
                chosen = rows
        if chosen is None:
            return None
        live = [r for r in chosen if r[3] is None or time_at < r[3]]
        return _best_level(live, side)


def _best_level(rows, side):
    prices = [r[1] for r in rows if r[0] == side]
    if not prices:
        return None
    top = max(prices) if side == "buy" else min(prices)
    total = sum(r[2] for r in rows if r[0] == side and r[1] == top)
    return f"{top}({total})"
