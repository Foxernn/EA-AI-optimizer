from mt5_realtime import MT5RealTime
import MetaTrader5 as mt5

def test_realtime_streaming():
    try:
        # Initialize real-time data handler
        rt_handler = MT5RealTime(symbol="USDJPY", timeframe=mt5.TIMEFRAME_M1)
        rt_handler.initialize()
        
        print(f"Starting real-time data stream for USDJPY...")
        
        # Stream data continuously
        for data in rt_handler.stream_data():
            # Process each new data point
            # Add your processing logic here
            pass
            
    except KeyboardInterrupt:
        print("\nStreaming stopped by user")
    except Exception as e:
        print(f"\nError in real-time streaming: {str(e)}")
    finally:
        mt5.shutdown()

if __name__ == "__main__":
    test_realtime_streaming()
