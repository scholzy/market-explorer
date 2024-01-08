from enum import Enum


class DBLibraries(Enum):
    Caches = "caches"
    Exchanges = "exchanges"


class DBSymbols(Enum):
    NasdaqTickers = "nasdaq_tickers"


class TSAnalyses(Enum):
    MACD = "MACD"