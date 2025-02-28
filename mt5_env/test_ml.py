import pandas as pd
from data_processor import TitanDataProcessor
import os
from model import TitanMLModel
from mt5_connector import MT5Connector
import MetaTrader5 as mt5

def get_mt5_data(connector):
    """Fetch data from MT5 instead of CSV"""
    try:
        # Fetch USDJPY data from MT5
        df = connector.get_real_time_data(
            symbol="USDJPY",
            timeframe=mt5.TIMEFRAME_M1,
            n_bars=30000  # Match similar size to CSV data
        )
        
        if df is None:
            raise Exception("Failed to fetch MT5 data")
            
        print(f"Fetched {len(df)} rows of MT5 data")
        print(f"Sample of MT5 data:\n{df.head()}")
        return df
        
    except Exception as e:
        print(f"Error fetching MT5 data: {str(e)}")
        raise

def test_ml_pipeline():
    processor = TitanDataProcessor()
    
    try:
        # Initialize MT5 connection
        connector = MT5Connector()
        if not connector.initialize_mt5():
            raise Exception("Failed to initialize MT5 connection")
        
        print("\nFetching MT5 data...")
        df = get_mt5_data(connector)
        
        # Process features
        print("\nGenerating features...")
        processed_data = processor.create_features(df)
        
        # Create target variable and align data
        processed_data = processed_data.dropna()
        y = (processed_data['Close'].shift(-1) > processed_data['Close']).astype(int)[:-1]
        processed_data = processed_data[:-1]
        
        # Prepare training data
        training_data = processor.prepare_training_data(processed_data)
        
        print("\nFeature generation complete")
        print(f"Generated features: {training_data.columns.tolist()}")
        print(f"Data shape: {training_data.shape}")
        print(f"Target shape: {y.shape}")
        
        # Train and evaluate model
        print("\nTraining model...")
        model = TitanMLModel()
        results = model.train(training_data, y)
        
        print("\nModel training results:")
        print(f"Accuracy: {results['accuracy']:.4f}")
        print(f"Precision: {results['precision']:.4f}")
        print(f"Recall: {results['recall']:.4f}")
        
    except Exception as e:
        print(f"\nError in ML pipeline: {str(e)}")
    finally:
        mt5.shutdown()

if __name__ == "__main__":
    print("Starting script...")
    try:
        test_ml_pipeline()
    except Exception as e:
        print(f"Main script error: {str(e)}")
    print("Script completed")
