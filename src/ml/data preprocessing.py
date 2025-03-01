def preprocess_raw_data(input_path):
    """Preprocess the raw USDJPY data into proper format"""
    try:
        # Read raw data with correct column names
        df = pd.read_csv(input_path, names=[
            'DateTime', 'Open', 'High', 'Low', 'Close', 'Volume'
        ], header=None)
        
        # Split DateTime into date and time parts
        df[['Date', 'Time']] = df['DateTime'].str.split('    ', expand=True)
        
        # Convert to datetime using the correct format
        df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], format='%Y.%m.%d %H:%M')
        
        # Drop temporary columns and set index
        df = df.drop(['Date', 'Time'], axis=1)
        df.set_index('DateTime', inplace=True)
        
        print(f"Processed {len(df)} rows of data")
        print(f"Sample of processed data:\n{df.head()}")
        return df
        
    except Exception as e:
        print(f"Error preprocessing data: {str(e)}")
        print(f"First few rows of raw data:\n{df.head()}")
        raise
