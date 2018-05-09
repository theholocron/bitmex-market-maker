import pytz
import settings
from dateutil import parser
from datetime import datetime
from bitmex.api import BitmexAPIConnector
from typing import Dict, Union, List


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

    def __init__(self, symbol: str='XBTUSD') -> None:
        """api call to return open positions for current account"""
        super().__init__()
        positions = self._make_request('GET', 'position', {"columns": self.COLUMNS})

        self.open_positions: List[BitmexPosition] = list()
        for position in positions:
            self.open_positions.append(BitmexPosition(position))


class BitmexPosition(object):

    def __init__(self, position: Dict[str, Union[str, int]]) -> None:
        self.symbol = None
        self.openingTimestamp = '1970-30-01 00:00:00Z'
        self.leverage = 0
        self.openingQty = 0
        self.currentQty = 0
        self.realisedCost = 0
        self.markPrice = 0
        self.realisedGrossPnl = 0
        self.unrealisedGrossPnl = 0
        self.simplePnl = 0
        self.liquidationPrice = 0
        self.lastPrice = 0
        self.breakEvenPrice = 0
        self.avgEntryPrice = 0
        self.prevClosePrice = 0

        for key, value in position.items():
            setattr(self, key, value)
        return

    def __repr__(self) -> str:
        sym = self.symbol
        qty = self.currentQty
        entry = int(self.avgEntryPrice)
        market = int(self.markPrice)
        liquid = int(self.liquidationPrice)
        rpnl = self.realisedGrossPnl / settings.XBt_to_XBT
        upnl = self.unrealisedGrossPnl / settings.XBt_to_XBT
        return f'<{sym}: {qty} Entry:{entry} Market:{market} Liquid:{liquid} rpnl: {rpnl} upnl: {upnl}>'

    @property
    def liquidation_delta(self) -> int:
        return int(self.liquidationPrice - self.markPrice)

    @property
    def tick(self) -> datetime:
        return pytz.utc.localize(parser.parse(self.openingTimestamp, ignoretz=True))

    @property
    def total_pnl(self) -> float:
        return (self.realisedGrossPnl + self.unrealisedGrossPnl) / settings.XBt_to_XBT
