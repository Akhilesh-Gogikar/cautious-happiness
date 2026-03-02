import backtrader as bt
import os
import sys
from logic.strategy import MovingAverageCross

def run_backtest():
    cerebro = bt.Cerebro()
    
    # Add dummy data
    data = bt.feeds.YahooFinanceCSVData(
        dataname='/root/cautious-happiness/strategies/moving_average_cross/data/sample.csv',
        fromdate=bt.datetime.datetime(2020, 1, 1),
        todate=bt.datetime.datetime(2020, 12, 31),
        reverse=False
    )
    cerebro.adddata(data)
    
    cerebro.addstrategy(MovingAverageCross)
    cerebro.broker.setcash(100000.0)
    
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

if __name__ == '__main__':
    run_backtest()
