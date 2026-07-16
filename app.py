# All the Libaries and Essential components used in the Application
from flask import Flask, render_template, request, jsonify
import pandas as pd
from werkzeug.utils import secure_filename
import os
from io import TextIOWrapper

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'   #Directory where uploaded files will be stored.
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB max

# Creates the uploads directory if it doesn’t already exist.
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Render to home page i.e index.html
@app.route('/')
def index():
    return render_template('index.html')

# Handles POST requests to /upload when a file is uploaded.
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    if file and file.filename.endswith('.csv'):
        try:
            stream = TextIOWrapper(file.stream)  #Converts binary file stream to text
            df = pd.read_csv(stream)  #Reads the file into a Pandas DataFrame (df).

            # Basic column check
            if 'Source' not in df.columns or 'Protocol' not in df.columns:
                return "CSV must have 'Source' and 'Protocol' columns.", 400

            top_sources = df['Source'].value_counts().head(5)    # Column includes IP addresses or device name
            top_protocols = df['Protocol'].value_counts().head(5)  # Column includes TCP, UDP, HTTP, etc

            # Sends the results back to the frontend in JSON format
            return jsonify({
                'top_sources': {
                    'labels': top_sources.index.tolist(),   # Name of source and protocol
                    'counts': top_sources.values.tolist()   # How often they appear
                },
                'top_protocols': {
                    'labels': top_protocols.index.tolist(),
                    'counts': top_protocols.values.tolist()
                }
            })
        except Exception as e:
            return f"Error processing file: {str(e)}", 500  # Show this message if there is some file format issue
    return "Invalid file type. Only CSV supported.", 400  # Show this if .csv file not found

if __name__ == '__main__':
     #app.run(host='127.0.0.1', port=5000, debug=True)  # Start the flask server (Developer Mode)
     app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))  # Start the flask server (Production Case)