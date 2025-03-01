import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import talib

class TitanDataProcessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    
    def process_mt5_data(self, mt5_data):
        """Process real-time MT5 data"""
        try:
            # Convert MT5 data format to match pipeline format
            df = pd.DataFrame(mt5_data)
            
            # Rename columns to match required format
            df = df.rename(columns={
                'time': 'DateTime',
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'tick_volume': 'Volume'
            })
            
            # Set DateTime as index
            df.set_index('DateTime', inplace=True)
            
            # Drop unnecessary MT5 columns
            df = df[self.required_columns]
            
            return df
            
        except Exception as e:
            print(f"Error processing MT5 data: {str(e)}")
            raise
    
    def create_features(self, data):
        """Generate technical indicators and features"""
        df = data.copy()
        
        # Add technical indicators
        df['RSI'] = talib.RSI(df['Close'])
        df['MA20'] = talib.SMA(df['Close'], timeperiod=20)
        df['MA50'] = talib.SMA(df['Close'], timeperiod=50)
        df['ATR'] = talib.ATR(df['High'], df['Low'], df['Close'])
        
        # Add custom features
        df['Price_Range'] = df['High'] - df['Low']
        df['Price_Change'] = df['Close'].pct_change()
        
        return df
    
    def prepare_training_data(self, data):
        """Prepare data for model training"""
        # Create explicit copy and remove NaN values
        df = data.copy()
        df = df.dropna()
        
        # Scale features using loc
        features = ['RSI', 'MA20', 'MA50', 'ATR', 'Price_Range', 'Price_Change']
        df.loc[:, features] = self.scaler.fit_transform(df[features])
        
        return df
    
    def process_realtime_data(self, mt5_data):
        """Process real-time data through the complete pipeline"""
        try:
            # Process MT5 data
            processed_df = self.process_mt5_data(mt5_data)
            
            # Generate features
            featured_df = self.create_features(processed_df)
            
            # Prepare for model
            prepared_df = self.prepare_training_data(featured_df)
            
            return prepared_df
            
        except Exception as e:
            print(f"Error in realtime processing: {str(e)}")
            return None
