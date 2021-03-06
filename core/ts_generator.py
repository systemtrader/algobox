# the purpose of these generators are to serve in place as real data
# for the purposes of testing and development while the data sources
# are not implemented

import uuid
import random

import datetime as dt

import numpy as np

import core.time
import core.format


class CandleTimeSeriesGenerator(object):
    """
    Random candle series. Not appropriate for testing strategies, only
    for testing the application itself.

    !TODO refactor to improve reuse

    Arguments:
        * dt_from (datetime) when to start
        * dt_to (datetime) when to finish
        * trading_hours (core)time.TradingHours; a TradingHours child class
            describing trading hours for the exchange of this thing.
        * interval (string, datetime.timedelta)
    """

    def __init__(self, dt_from, dt_to, trading_hours, interval, topic):
        self.start = dt_from
        self.end = dt_to
        self.topic = topic

        # str is now equivalent to basestring for str type checking in py3?
        if isinstance(interval, str):
            interval = core.time.interval_string_to_time_delta(interval)
        self.interval = interval

        self.previous_candle = None
        self.trading_hours = trading_hours

    def __iter__(self):
        return self

    def __next__(self):
        stdev = 0.03
        try:
            this_dt = self.previous_candle.datetime
        except:
            this_dt = self.start

        while this_dt <= self.end:
            if not self.previous_candle:
                if self.trading_hours.open_at(self.start):
                    this_dt = self.start
                else:
                    this_dt = self.trading_hours.next_open(self.start)

                mean = random.randint(20, 250)
                random_prices = list(np.random.normal(loc=mean, scale=stdev, size=64))
                random_prices = sorted({round(p, 2) for p in random_prices})

                # we could ensure open and close are unique by popping the
                # selected value, but it's not particularly important or realistic
                new_candle = core.format.Candle(
                    this_dt=this_dt,
                    topic=self.topic,
                    high=random_prices[-1],
                    low=random_prices[0],
                    open=random.choice(random_prices[1:-2]),
                    close=random.choice(random_prices[1:-2]),
                    volume=random.randint(1000, 100000)
                )
                self.previous_candle = new_candle

                return new_candle

            this_dt = self.previous_candle.datetime + self.interval
            if not self.trading_hours.open_at(this_dt):
                this_dt = self.trading_hours.next_open(this_dt)

            mean = self.previous_candle.close
            random_prices = list(np.random.normal(loc=mean, scale=stdev, size=64))
            random_prices = sorted({round(p, 2) for p in random_prices})

            new_candle = core.format.Candle(
                this_dt=this_dt,
                topic=self.topic,
                high=random_prices[-1],
                low=random_prices[0],
                open=self.previous_candle.close,
                close=random.choice(random_prices[1:-2]),
                volume=random.randint(1000, 100000)
            )
            self.previous_candle = new_candle

            return new_candle
        raise StopIteration()
