from mt5_connector import MT5Connector
import MetaTrader5 as mt5

def test_mt5_connection():
    # Initialize connector
    connector = MT5Connector()
    
    try:
        # Connect to MT5
        if not connector.initialize_mt5():
            return
        
        # Login to account (replace with your credentials)
        login_success = connector.login_account(
            login=10005329908,
            password="6!DjRbZa",
            server="MetaQuotes-Demo"
        )
        
        if not login_success:
            return
            
        # Fetch real-time USDJPY data
        data = connector.get_real_time_data(
            symbol="USDJPY",
            timeframe=mt5.TIMEFRAME_M1,
            n_bars=100
        )
        
        if data is not None:
            print("\nLatest USDJPY data:")
            print(data.tail())
            
    except Exception as e:
        print(f"Error in MT5 test: {str(e)}")
    finally:
        mt5.shutdown()

if __name__ == "__main__":
    test_mt5_connection()
