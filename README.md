# PDF Q&A Assistant

A simple Gradio-based application that lets you upload a PDF and ask questions about its content. The app uses natural language processing to find relevant answers from the document.

## Features

- Upload any PDF document
- Ask questions in natural language
- Get relevant answers extracted from the document
- Simple and intuitive web interface

## Installation

1. Clone this repository
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python app.py
   ```
2. Open your web browser and navigate to `http://localhost:7860`
3. Upload a PDF file and click "Process PDF"
4. Once processed, type your question in the text box and click "Ask"

## How It Works

1. The application extracts text from the uploaded PDF
2. The text is split into manageable chunks
3. Each chunk is converted into a vector embedding using HuggingFace's Instructor model
4. When you ask a question, the system finds the most relevant text chunks using vector similarity
5. The most relevant chunk is returned as the answer

## Requirements

- Python 3.8+
- See `requirements.txt` for Python package dependencies

## Note

- The first time you run the app, it will download the HuggingFace model (about 1.5GB)
- Processing large PDFs may take some time depending on your system
- For best results, ask specific questions about the document content
