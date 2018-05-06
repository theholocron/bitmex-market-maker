class RetryLimitExceededError(Exception):
    pass


class MarketOverloadError(Exception):
    pass


class APIParameterError(Exception):
    pass


class UnauthorizedError(Exception):
    pass
