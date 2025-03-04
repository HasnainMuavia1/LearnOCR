import base64
from flask import Flask, request, jsonify, render_template
from groq import Groq
import os
from dotenv import load_dotenv
import PyPDF2
from docx import Document
import tempfile

load_dotenv()

app = Flask(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def process_pdf(file):
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return None


def process_docx(file):
    """Extract text from DOCX file"""
    try:
        doc = Document(file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error processing DOCX: {str(e)}")
        return None


def process_text(file):
    """Extract text from TXT file"""
    try:
        text = file.read().decode('utf-8')
        return text.strip()
    except Exception as e:
        print(f"Error processing TXT: {str(e)}")
        return None


def process_doc(file):
    """Extract text from DOC file by saving it as temporary file"""
    try:
        # Create a temporary file to save the uploaded content
        with tempfile.NamedTemporaryFile(delete=False, suffix='.doc') as temp_file:
            file.save(temp_file.name)
            # Use antiword or other DOC processor here
            # For now, we'll return a message that DOC files aren't supported yet
            return "DOC file format is not supported yet. Please convert to DOCX."
    except Exception as e:
        print(f"Error processing DOC: {str(e)}")
        return None
    finally:
        if 'temp_file' in locals():
            os.unlink(temp_file.name)


def get_document_text(file):
    """Process file based on its extension and return the text content"""
    if not file:
        return None

    filename = file.filename.lower()
    file.seek(0)  # Reset file pointer to beginning

    if filename.endswith('.pdf'):
        return process_pdf(file)
    elif filename.endswith('.docx'):
        return process_docx(file)
    elif filename.endswith('.doc'):
        return process_doc(file)
    elif filename.endswith('.txt'):
        return process_text(file)
    else:
        return None


# Route to render the language.html file
@app.route('/')
def index():
    return render_template('index.html')


# Route to handle the chat request
@app.route('/process_message', methods=['POST'])
def chat_stream():
    try:
        # Get form data
        model = request.form.get('model', 'mixtral-8x7b-32768')
        message = request.form.get('message')
        
        print(f"Received message: {message}")
        print(f"Selected model: {model}")
        
        if not message:
            print("No message provided")
            return jsonify({
                'status': 'error',
                'message': 'No message provided'
            }), 400

        try:
            response = generate_response(model, message)
            print(f"Generated response: {response}")
            
            if not response:
                raise Exception("Empty response from model")
                
            return jsonify({
                'status': 'success',
                'response': response
            })
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f"Error generating response: {str(e)}"
            }), 500
            
    except Exception as e:
        print(f"Error in chat_stream: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

def generate_response(model, query) -> str:
    try:
        print(f"Generating response with model: {model}")
        print(f"Query: {query}")
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant specialized in coding and study-related responses."

                },
                {
                    "role": "user",
                    "content": query,
                }
            ],
            model=model,
            temperature=0.5,
            max_tokens=1024,
            top_p=1,
            stop=None,
            stream=False,
        )
        
        response = chat_completion.choices[0].message.content
        print(f"Generated response: {response}")
        return response
        
    except Exception as e:
        print(f"Error in generate_response: {str(e)}")
        raise e

@app.route('/vision-stream', methods=['POST'])
def vision_stream():
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400

        model = data.get('model', 'llava-13b')
        image = data.get('image')

        if not image:
            return jsonify({
                'status': 'error',
                'message': 'No image provided'
            }), 400

        return jsonify({
            'status': 'success',
            'response': generate_vision_response(model, image)
        })
    except Exception as e:
        print("Error:", str(e))
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400


@app.route('/process_file', methods=['POST'])
def process_file():
    try:
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No file provided'
            }), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'No file selected'
            }), 400

        # Get optional query parameter
        query = request.form.get('query', '')
        model = request.form.get('model', 'mixtral-8x7b-32768')

        # Extract text from the document
        text = get_document_text(file)
        if not text:
            return jsonify({
                'status': 'error',
                'message': 'Could not extract text from the file'
            }), 400

        # If query is provided, use it to get specific information from the text
        if query:
            prompt = f"Document content: {text}\n\nUser query: {query}\n\nPlease answer the query based on the document content."
        else:
            prompt = f"Please analyze and summarize the following document content:\n\n{text}"

        response = generate_response(model, prompt)
        
        return jsonify({
            'status': 'success',
            'response': response
        })

    except Exception as e:
        print(f"Error in process_file: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400




def generate_vision_response(model, img):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What do you see in this image?"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": img,
                            },
                        },
                    ],
                }
            ],
            model=model,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error in generate_vision_response: {str(e)}")
        raise e



if __name__ == '__main__':
    app.run(debug=True)
