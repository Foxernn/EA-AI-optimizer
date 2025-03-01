import os
import chardet  # Install with: pip install chardet
from datetime import datetime


class TitanEAParser:
    def __init__(self):
        self.metadata = {}

    def parse_set_file(self, file_path):
        """
        Parse a SET file for EA parameters, dynamically detecting the file's encoding.
        """
        try:
            # Detect file encoding
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                detected = chardet.detect(raw_data)
                encoding = detected['encoding']

            # Read the file with the detected encoding
            settings = {
                'raw_lines': [],
                'parameters': {},
                'metadata': {}
            }
            with open(file_path, 'r', encoding=encoding) as f:
                lines = [line.strip() for line in f if line.strip()]
                settings['raw_lines'] = lines

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
                    settings['parameters'][key] = {
                        "section": current_section,
                        "value": value,
                        "raw_line": line
                    }

            # Return structured data
            return {
                "file_name": os.path.basename(file_path),
                "file_type": "SET File",
                "settings": settings,
                "line_count": len(lines),
                "parameter_count": len(settings['parameters']),
                "creation_date": datetime.fromtimestamp(
                    os.path.getctime(file_path)
                ).strftime('%Y-%m-%d %H:%M:%S')
            }

        except Exception as e:
            return {
                "file_name": os.path.basename(file_path),
                "file_type": "SET File",
                "error": str(e),
                "raw_content": []
            }


# Example usage:
# parser = TitanEAParser()
# result = parser.parse_set_file("path/to/your/set/file.set")
# print(result)
