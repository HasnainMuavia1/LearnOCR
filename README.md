# LearnOCR

A modern web application for intelligent document analysis using Groq's AI models. The application supports processing various file types including images, PDFs, Excel files, and text documents.

## Features

- Modern and responsive UI
- Drag and drop file upload
- Support for multiple file types:
  - Images (JPG, PNG, etc.)
  - PDF documents
  - Excel spreadsheets
  - Text files
- Intelligent analysis using Groq AI models
- Custom query support for each file type

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the root directory and add your Groq API key:
```
GROQ_API_KEY=your_api_key_here
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to `http://localhost:5000`

## Usage

1. Select the mode (Playground/LearnOCR) and model from the dropdowns
2. Drag and drop or click to upload your file
3. (Optional) Enter a custom query for analysis
4. Click "Process" to analyze the file
5. View the results below the form

## File Type Support

- **Images**: Automatically processed using vision model for content analysis
- **PDFs**: Text is extracted and analyzed
- **Excel**: Spreadsheet data is converted to text for analysis
- **Text**: Direct text analysis

Created with ❤️ by Hasnain Muavia
