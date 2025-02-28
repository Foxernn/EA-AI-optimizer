import MetaTrader5 as mt5
import pandas as pd
import time
from datetime import datetime

class MT5RealTime:
    def __init__(self, symbol="USDJPY", timeframe=mt5.TIMEFRAME_M1):
        self.symbol = symbol
        self.timeframe = timeframe
        self.last_time = None
        
    def initialize(self):
        """Initialize MT5 connection"""
        if not mt5.initialize():
            raise Exception(f"MT5 initialization failed: {mt5.last_error()}")
        print("MT5 initialized successfully")
        print(f"MT5 version: {mt5.version()}")
    
    def get_realtime_data(self, bars=100):
        """Get current market data"""
        try:
            rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, bars)
            if rates is None:
                raise Exception("Failed to get market data")
            
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)
            
            # Rename columns to match existing pipeline
            df = df.rename(columns={
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'tick_volume': 'Volume'
            })
            
            return df
            
        except Exception as e:
            print(f"Error getting real-time data: {str(e)}")
            return None

    def stream_data(self):
        """Stream market data continuously"""
        while True:
            try:
                current_data = self.get_realtime_data(bars=1)
                if current_data is not None:
                    current_time = current_data.index[-1]
                    if self.last_time != current_time:
                        self.last_time = current_time
                        print(f"\nNew data at: {current_time}")
                        print(current_data)
                        yield current_data
                time.sleep(1)
                
            except Exception as e:
                print(f"Error streaming data: {str(e)}")
                time.sleep(5)

if __name__ == "__main__":
    try:
        rt = MT5RealTime()
        rt.initialize()
        print(f"Starting real-time data stream for USDJPY...")
        for data in rt.stream_data():
            pass
    except KeyboardInterrupt:
        print("\nStreaming stopped by user")
    finally:
        mt5.shutdown()
