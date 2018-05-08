import os
import pytz
from dateutil import parser
from bitmex.api import BitmexAPIConnector


class BitmexPositionAPI(BitmexAPIConnector):

    COLUMNS = [
        'symbol',
        'leverage',
        'openingTimestamp',
        'openingQty',
        'currentQty',
        'realisedCost',
        'markPrice',
        'realisedGrossPnl',
        'unrealisedGrossPnl',
        'simplePnl',
        'liquidationPrice',
        'lastPrice',
        'breakEvenPrice',
        'avgEntryPrice',
        'prevClosePrice'
        ]

    def __init__(self, symbol='XBTUSD'):
        """api call to return open positions for current account"""
        super().__init__()
        positions = self._make_request('GET', 'position', {"columns": self.COLUMNS})

        self.open_positions = list()
        for position in positions:
            self.open_positions.append(BitmexPosition(position))


class BitmexPosition(object):

    def __init__(self, position):
        self.XBt_to_XBT = int(os.getenv('XBt_to_XBT'))
        for key, value in position.items():
            setattr(self, key, value)

    def __repr__(self):
        sym = self.symbol
        qty = self.currentQty
        entry = int(self.avgEntryPrice)
        market = int(self.markPrice)
        liquid = int(self.liquidationPrice)
        rpnl = self.realisedGrossPnl / self.XBt_to_XBT
        upnl = self.unrealisedGrossPnl / self.XBt_to_XBT
        return f'<{sym}: {qty} Entry:{entry} Market:{market} Liquid:{liquid} rpnl: {rpnl} upnl: {upnl}>'

    @property
    def liquidation_delta(self):
        return (self.liquidationPrice - self.markPrice)

    @property
    def tick(self):
        return pytz.utc.localize(parser.parse(self.openingTimestamp, ignoretz=True))

    @property
    def total_pnl(self):
        return (self.realisedGrossPnl + self.unrealisedGrossPnl) / self.XBt_to_XBT
