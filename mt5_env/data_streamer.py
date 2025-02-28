import MetaTrader5 as mt5
import pandas as pd
import time
from datetime import datetime

class DataStreamer:
    def __init__(self, symbol="USDJPY", timeframe=mt5.TIMEFRAME_M1):
        self.symbol = symbol
        self.timeframe = timeframe
        self.last_time = None
        
    def initialize(self):
        if not mt5.initialize():
            raise Exception(f"MT5 initialization failed: {mt5.last_error()}")
        print("MT5 initialized successfully")
    
    def stream_data(self, bars=100):
        """Stream market data continuously"""
        while True:
            try:
                # Get current data
                rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, bars)
                if rates is None:
                    raise Exception("Failed to get market data")
                
                df = pd.DataFrame(rates)
                df['time'] = pd.to_datetime(df['time'], unit='s')
                
                # Check if we have new data
                current_time = df['time'].iloc[-1]
                if self.last_time != current_time:
                    self.last_time = current_time
                    print(f"New data received at: {current_time}")
                    yield df
                    
                time.sleep(1)  # Wait 1 second before next check
                
            except Exception as e:
                print(f"Error streaming data: {str(e)}")
                time.sleep(5)  # Wait longer on error
