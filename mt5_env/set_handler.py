import os
import json

class SetFileHandler:
    def __init__(self, set_file_path):
        self.set_file_path = set_file_path
        self.parameters = {}
        self.load_set_file()
    
    def load_set_file(self):
        """Load parameters from SET file"""
        try:
            with open(self.set_file_path, 'r') as file:
                for line in file:
                    if '=' in line:
                        key, value = line.strip().split('=')
                        self.parameters[key.strip()] = value.strip()
            print(f"Loaded {len(self.parameters)} parameters from SET file")
        except Exception as e:
            print(f"Error loading SET file: {str(e)}")
    
    def update_parameters(self, predictions):
        """Update parameters based on ML predictions"""
        try:
            # Example parameter adjustment logic
            if predictions['trend_strength'] > 0.7:
                self.parameters['TakeProfit'] = str(int(float(self.parameters['TakeProfit']) * 1.2))
                self.parameters['StopLoss'] = str(int(float(self.parameters['StopLoss']) * 0.8))
            
            # Save updated parameters
            self.save_set_file()
            
        except Exception as e:
            print(f"Error updating parameters: {str(e)}")
    
    def save_set_file(self):
        """Save parameters back to SET file"""
        try:
            with open(self.set_file_path, 'w') as file:
                for key, value in self.parameters.items():
                    file.write(f"{key}={value}\n")
            print("SET file updated successfully")
        except Exception as e:
            print(f"Error saving SET file: {str(e)}")
