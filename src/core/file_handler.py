import os
import chardet  # Install with: pip install chardet

class FileHandler:
    def __init__(self):
        self.supported_extensions = ['.ex5', '.set']

    def process_file(self, file_path):
        """Process uploaded EA or SET files."""
        if file_path.endswith('.ex5'):
            return self.process_ex5_file(file_path)
        elif file_path.endswith('.set'):
            return self.process_set_file(file_path)
        else:
            raise ValueError("Unsupported file type")

    def process_ex5_file(self, file_path):
        """Process .ex5 files (placeholder for actual logic)."""
        # Add logic for .ex5 files if needed
        return {"file_name": os.path.basename(file_path), "file_type": "EX5 File"}

    def process_set_file(self, file_path):
        """Process SET file containing EA parameters."""
        parameters = {}
        try:
            # Detect encoding
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                detected = chardet.detect(raw_data)
                encoding = detected['encoding']

            # Read the file with the detected encoding
            with open(file_path, 'r', encoding=encoding) as f:
                lines = [line.strip() for line in f if line.strip()]

            # Parse each line
            current_section = "General"
            for line in lines:
                # Skip comments or section headers
                if line.startswith(';'):
                    if "=====" in line:
                        current_section = line.replace(';', '').replace('=', '').strip()
                    continue

                # Parse key-value pairs
                if '=' in line:
                    key, value = line.split('=', 1)  # Split only on the first '='
                    key = key.strip()
                    value = value.split('||')[0].strip()  # Extract value before "||"
                    parameters[key] = {
                        "section": current_section,
                        "value": value,
                        "raw_line": line
                    }

            return {
                "file_name": os.path.basename(file_path),
                "file_type": "SET File",
                "parameters": parameters,
                "line_count": len(lines),
                "parameter_count": len(parameters),
            }
        except Exception as e:
            raise Exception(f"Error processing SET file: {str(e)}")
