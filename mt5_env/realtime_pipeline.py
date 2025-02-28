import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
from data_processor import TitanDataProcessor
from model import TitanMLModel
import time

class TitanSetFileParser:
    def __init__(self):
        self.settings = {
            'basic': {},
            'entry': {},
            'exit': {},
            'take_profit': {},
            'stop_loss': {},
            'schedule': {},
            'news': {}
        }
        
    def read_set_file(self, filepath):
        try:
            with open(filepath, 'r') as file:
                current_section = 'basic'
                for line in file:
                    line = line.strip()
                    if not line or line.startswith(';'):
                        continue
                        
                    if line.startswith('=====') and line.endswith('====='):
                        section_name = line.replace('=', '').strip().lower()
                        if 'basic' in section_name:
                            current_section = 'basic'
                        elif 'entry' in section_name:
                            current_section = 'entry'
                        elif 'exit' in section_name:
                            current_section = 'exit'
                        elif 'take profit' in section_name:
                            current_section = 'take_profit'
                        elif 'stop loss' in section_name:
                            current_section = 'stop_loss'
                        elif 'schedule' in section_name:
                            current_section = 'schedule'
                        elif 'news' in section_name:
                            current_section = 'news'
                        continue
                        
                    if '=' in line:
                        name, value = line.split('=', 1)
                        if '||' in value:
                            value = value.split('||')[0]
                        self.settings[current_section][name] = value
            return True
            
        except Exception as e:
            print(f"Error reading set file: {str(e)}")
            return False

class RealtimePipeline:
    def __init__(self):
        self.processor = TitanDataProcessor()
        self.model = TitanMLModel()
        self.set_parser = TitanSetFileParser()
        
    def initialize_mt5(self):
        if not mt5.initialize():
            raise Exception(f"MT5 initialization failed: {mt5.last_error()}")
            
        authorized = mt5.login(
            login=51614441,
            password="%NCy@Z2A",
            server="VantageInternational-Live 4"
        )
        
        if not authorized:
            raise Exception(f"MT5 login failed: {mt5.last_error()}")
        print("MT5 initialized and logged in successfully")
        
    def preprocess_mt5_data(self, rates):
        try:
            df = pd.DataFrame(rates)
            
            if isinstance(df['time'].iloc[0], (int, float)):
                df['DateTime'] = pd.to_datetime(df['time'], unit='s')
            else:
                df['DateTime'] = pd.to_datetime(df['time'])
                
            df.set_index('DateTime', inplace=True)
            
            df = df.rename(columns={
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'tick_volume': 'Volume'
            })
            
            df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
            df = df.astype(float)
            
            print(f"Processed {len(df)} rows of data")
            print(f"Sample of processed data:\n{df.head()}")
            return df
            
        except Exception as e:
            print(f"Error preprocessing data: {str(e)}")
            print(f"First few rows of raw data:\n{df.head()}")
            raise
        
    def get_historical_data(self, symbol):
        try:
            self.initialize_mt5()
            
            if not mt5.symbol_select(symbol, True):
                raise Exception(f"Failed to select {symbol} in Market Watch")
            
            print(f"Downloading historical data for {symbol}...")
            
            print("Fetching H4 data for full period...")
            h4_rates = mt5.copy_rates_from(
                symbol,
                mt5.TIMEFRAME_H4,
                datetime.now(),
                2190
            )
            
            if h4_rates is None or len(h4_rates) == 0:
                raise Exception(f"Failed to fetch H4 data for {symbol}")
            
            h4_df = pd.DataFrame(h4_rates)
            h4_df['time'] = pd.to_datetime(h4_df['time'], unit='s')
            h4_df.set_index('time', inplace=True)
            
            print("Fetching recent M1 data in chunks...")
            m1_chunks = []
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
            
            current_date = start_date
            while current_date < end_date:
                next_date = min(current_date + timedelta(days=3), end_date)
                print(f"Fetching M1 data for: {current_date.strftime('%Y-%m-%d')} to {next_date.strftime('%Y-%m-%d')}")
                
                chunk = mt5.copy_rates_range(
                    symbol,
                    mt5.TIMEFRAME_M1,
                    current_date,
                    next_date
                )
                
                if chunk is not None and len(chunk) > 0:
                    chunk_df = pd.DataFrame(chunk)
                    chunk_df['time'] = pd.to_datetime(chunk_df['time'], unit='s')
                    chunk_df.set_index('time', inplace=True)
                    m1_chunks.append(chunk_df)
                    print(f"Fetched {len(chunk)} M1 records")
                
                current_date = next_date
                time.sleep(0.1)
            
            if m1_chunks:
                print("Combining H4 and M1 data...")
                m1_df = pd.concat(m1_chunks)
                final_df = pd.concat([h4_df, m1_df])
                final_df = final_df[~final_df.index.duplicated(keep='last')]
                final_df = final_df.sort_index()
            else:
                print("Using H4 data only...")
                final_df = h4_df
            
            df = self.preprocess_mt5_data(final_df.reset_index().to_dict('records'))
            
            print(f"Total records: {len(df)}")
            print(f"Full date range: {df.index[0]} to {df.index[-1]}")
            
            return df
                
        except Exception as e:
            print(f"Error fetching historical data: {str(e)}")
            return None
    
    def analyze_set_file(self, set_file_path, historical_data):
        if not self.set_parser.read_set_file(set_file_path):
            return None
            
        recommendations = {}
        for section, params in self.set_parser.settings.items():
            for param, value in params.items():
                if '||' in str(value) and str(value).endswith('Y'):
                    current_val = float(value.split('||')[0])
                    min_val = float(value.split('||')[2])
                    max_val = float(value.split('||')[3])
                    recommendations[param] = {
                        'current': current_val,
                        'min': min_val,
                        'max': max_val
                    }
        return recommendations
    
    def process_symbols(self, symbols=['USDJPY', 'XAUUSD']):
        try:
            for symbol in symbols:
                print(f"\nProcessing {symbol}...")
                historical_data = self.get_historical_data(symbol)
                
                if historical_data is not None:
                    featured_data = self.processor.create_features(historical_data)
                    processed_data = self.processor.prepare_training_data(featured_data)
                    
                    y = (processed_data['Close'].shift(-1) > processed_data['Close']).astype(int)[:-1]
                    processed_data = processed_data[:-1]
                    
                    results = self.model.train(processed_data, y)
                    
                    print(f"Generated features shape: {processed_data.shape}")
                    print(f"Sample of processed data:\n{processed_data.head()}")
                    print("\nModel training results:")
                    print(f"Accuracy: {results['accuracy']:.4f}")
                    print(f"Precision: {results['precision']:.4f}")
                    print(f"Recall: {results['recall']:.4f}")
                    
        except Exception as e:
            print(f"Error in processing: {str(e)}")
        finally:
            mt5.shutdown()

if __name__ == "__main__":
    pipeline = RealtimePipeline()
    pipeline.process_symbols()
