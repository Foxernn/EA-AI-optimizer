import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime

class MT5Connector:
    def __init__(self):
        self.connected = False
        
    def initialize_mt5(self):
        """Initialize MT5 connection"""
        if not mt5.initialize():
            print(f"MT5 initialization failed: {mt5.last_error()}")
            return False
            
        print(f"MT5 version: {mt5.version()}")
        self.connected = True
        return True
    
    def login_account(self, login, password, server):
        """Login to MT5 account"""
        if not self.connected:
            print("MT5 not initialized")
            return False
            
        authorized = mt5.login(login=login, 
                             password=password,
                             server=server)
        
        if authorized:
            print(f"Connected to account #{login}")
            account_info = mt5.account_info()
            if account_info is not None:
                print(f"Balance: {account_info.balance}")
                print(f"Equity: {account_info.equity}")
            return True
        else:
            print(f"Failed to connect: {mt5.last_error()}")
            return False
    
    def get_real_time_data(self, symbol, timeframe, n_bars=100):
        """Fetch real-time market data"""
        if not self.connected:
            return None
            
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, n_bars)
        if rates is not None:
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            return df
        return None
