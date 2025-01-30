from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import os
import json
from PyPDF2 import PdfReader
from rag_system import RAGSystem

app = Flask(__name__)

app.secret_key = '12345' 
app.config['UPLOAD_FOLDER'] = 'uploads/'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Global RAG instance
rag_system = None

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    reader = PdfReader(pdf_path)
    text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    return text

import re

def extract_structured_data(text):
    """Extract structured data (like email, phone, certifications, etc.) from the raw text."""
    
    structured_data = {
        'name': None,
        'email': None,
        'phone': None,
        'certifications': [],
        'education': None,
        'projects': []
    }

    # Regex for email and phone
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    phone_pattern = r'\+?[0-9]{1,4}?[-.\s]?\(?\d{1,4}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}'
    
    # Extract email
    structured_data['email'] = re.findall(email_pattern, text)
    structured_data['phone'] = re.findall(phone_pattern, text)

    # Extract name (assuming the first line might have the name)
    structured_data['name'] = text.split("\n")[0].strip()  # Assuming the name is the first line

    # Extract certifications (look for "CERTIFICATIONS" or similar keywords)
    cert_pattern = r'(?<=CERTIFICATIONS)(.*?)(?=EDUCATION|PROJECTS|$)'  # Modify based on exact resume format
    certifications = re.findall(cert_pattern, text, re.DOTALL)
    if certifications:
        structured_data['certifications'] = certifications[0].strip().split('\n')

    # Extract education (look for "EDUCATION" or similar keywords)
    education_pattern = r'(?<=EDUCATION)(.*?)(?=PROJECTS|CERTIFICATIONS|$)'
    education = re.findall(education_pattern, text, re.DOTALL)
    if education:
        structured_data['education'] = education[0].strip()

    # Extract projects (look for "PROJECTS" or similar keywords)
    projects_pattern = r'(?<=PROJECTS)(.*?)(?=INTERNSHIP|$)'
    projects = re.findall(projects_pattern, text, re.DOTALL)
    if projects:
        structured_data['projects'] = projects[0].strip().split('\n')

    return structured_data



def save_structured_data(structured_data):
    # Save structured data to a JSON file
    with open(os.path.join(app.config['UPLOAD_FOLDER'], 'structured_data.json'), 'w', encoding='utf-8') as f:
        json.dump(structured_data, f)


@app.route('/', methods=['GET', 'POST'])
def index():
    global rag_system
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)

            # Store file path in session
            session['file_path'] = file_path

            # Extract and save text
            corpus_text = extract_text_from_pdf(file_path)
            structured_data = extract_structured_data(corpus_text)

            # Save structured data to JSON file
            save_structured_data(structured_data)

            # Initialize RAG system with the structured data
            rag_system = RAGSystem(os.path.join(app.config['UPLOAD_FOLDER'], 'structured_data.json'))

            return redirect(url_for('index'))

    return render_template('index.html', rag_system=rag_system is not None, file_uploaded=session.get('file_path'))


@app.route('/query', methods=['POST'])
@app.route('/query', methods=['POST'])
def query():
    global rag_system
    if not rag_system:
        return jsonify({'error': 'Please upload a PDF first.'}), 400

    user_query = request.form['query']
    if not user_query:
        return jsonify({'error': 'Please enter a query.'}), 400

    # Load structured data
    with open(os.path.join(app.config['UPLOAD_FOLDER'], 'structured_data.json'), 'r', encoding='utf-8') as f:
        structured_data = json.load(f)

    # Checking for common phrases in the query
    user_query = user_query.lower()

    if 'email' in user_query:
        return jsonify({'answer': f"Atique's email is {structured_data['email']}"})
    elif 'phone' in user_query or 'contact' in user_query:
        return jsonify({'answer': f"Atique's phone number is {structured_data['phone']}"})
    elif 'certification' in user_query:
        certifications = ", ".join(structured_data['certifications'])
        return jsonify({'answer': f"Atique's certifications: {certifications}"})
    elif 'education' in user_query:
        return jsonify({'answer': f"Atique studied at {structured_data['education']}"})
    elif 'project' in user_query:
        return jsonify({'answer': f"Atique worked on projects like {', '.join(structured_data['projects'])}"})
    else:
        return jsonify({'error': 'Query not understood.'}), 400




if __name__ == '__main__':
    app.run(debug=True)
