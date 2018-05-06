import os
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
        return f'<{self.symbol}: {self.currentQty} Entry:{int(self.avgEntryPrice)} Market:{int(self.markPrice)} Liquid:{int(self.liquidationPrice)} rpnl: {self.realisedGrossPnl/self.XBt_to_XBT} upnl: {self.unrealisedGrossPnl/self.XBt_to_XBT}>'
