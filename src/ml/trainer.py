from data_processor import TitanDataProcessor
from model import TitanMLModel
from sklearn.model_selection import GridSearchCV

class ModelTrainer:
    def __init__(self):
        self.data_processor = TitanDataProcessor()
        self.model = TitanMLModel()

    def train_model(self, data):
        """Complete training pipeline"""
        try:
            print("Processing features...")
            # Create features and prepare data
            processed_data = self.data_processor.create_features(data)
            training_data = self.data_processor.prepare_training_data(processed_data)
            
            # Define target variable (1 if price goes up, 0 if down)
            y = (training_data['Close'].shift(-1) > training_data['Close']).astype(int)[:-1]
            training_data = training_data[:-1]  # Remove last row to match y length
            
            # Train and evaluate
            print("Training model...")
            results = self.model.train(training_data, y)
            return results

        except Exception as e:
            print(f"Error in training pipeline: {str(e)}")
            return None

    def optimize_parameters(self, X, y):
        """Optimize model hyperparameters"""
        try:
            print("Starting parameter optimization...")
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_depth': [5, 10, 15],
                'min_samples_split': [2, 5, 10]
            }

            grid_search = GridSearchCV(
                self.model.model,
                param_grid,
                cv=5,
                scoring='accuracy'
            )

            grid_search.fit(X[self.model.feature_columns], y)
            return grid_search.best_params_

        except Exception as e:
            print(f"Error in parameter optimization: {str(e)}")
            return None
