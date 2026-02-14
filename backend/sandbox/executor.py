import sys
import backtrader as bt
import pandas as pd
import json
import os
import importlib.util

def load_strategy_from_code(code_str):
    # Dynamic module loading from string
    spec = importlib.util.spec_from_loader('user_strategy', loader=None)
    module = importlib.util.module_from_spec(spec)
    exec(code_str, module.__dict__)
    
    # Find the class that inherits from bt.Strategy
    for name, obj in module.__dict__.items():
        if isinstance(obj, type) and issubclass(obj, bt.Strategy) and obj is not bt.Strategy:
            return obj
    return None

def run_backtest(strategy_class, data_path='/app/data/data.csv'):
    cerebro = bt.Cerebro()
    cerebro.addstrategy(strategy_class)
    
    # Load Data (Mock data generation if file missing for now)
    if os.path.exists(data_path):
        data = bt.feeds.GenericCSVData(dataname=data_path)
        cerebro.adddata(data)
    else:
        # Create mock data
        data = bt.feeds.BacktraderCSVData(dataname='mock_data.csv') # Placeholder
        print("Data file not found, creating dummy cerebro run for syntax check")

    cerebro.broker.setcash(100000.0)
    
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    final_value = cerebro.broker.getvalue()
    print('Final Portfolio Value: %.2f' % final_value)
    
    return {
        "final_value": final_value,
        "pnl": final_value - 100000.0
    }

if __name__ == "__main__":
    # Expecting code passed via environment variable or file
    # For now, we'll read from a file mounted at /app/strategy.py
    
    try:
        with open('/app/strategy.py', 'r') as f:
            code = f.read()
            
        strategy = load_strategy_from_code(code)
        if not strategy:
            print("No valid strategy class found.")
            sys.exit(1)
            
        result = run_backtest(strategy)
        print(json.dumps(result))
        
    except Exception as e:
        print(f"Execution Error: {e}")
        sys.exit(1)
