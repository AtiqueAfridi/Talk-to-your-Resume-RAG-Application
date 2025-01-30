# Resume Data Extraction with Flask and RAG System

This project is a web application built with Flask that allows you to upload a PDF resume, extract structured information from it, and query the extracted data using a RAG (Retrieve and Generate) system. It aims to assist users in querying important details from resumes like name, email, skills, education, etc.

## Features

- Upload PDF resumes.
- Extract key data from resumes (e.g., Name, Email, Education, etc.).
- Query the extracted data using natural language questions.
- Retrieve structured data in a user-friendly format.

## Requirements

- Python 3.x
- Flask
- PyPDF2

To install the required dependencies, run:

```bash
pip install -r requirements.txt
Setup
Clone the repository:

bash
Copy
Edit
git clone <repository_url>
cd <project_directory>
Install the dependencies:

bash
Copy
Edit
pip install -r requirements.txt
Create an uploads/ folder in the project directory where the uploaded PDFs will be saved:

bash
Copy
Edit
mkdir uploads
Set the SECRET_KEY in the Flask app to something secure for session management.

Running the Application
Start the Flask development server:

bash
Copy
Edit
python app.py
The application will be running on http://127.0.0.1:5000/.

You can now upload your resume in PDF format. After uploading, you can ask questions about the resume, such as "What is the email?" or "What are the certifications?"

Example Queries
"What is the email of Atique?"
"What is the education history?"
"What certifications has Atique completed?"
Project Structure
bash
Copy
Edit
/project-directory
  /uploads          # Folder for storing uploaded PDFs
  app.py            # Main Flask application
  requirements.txt  # Dependencies for the project
  README.md         # Project description
  /rag_system       # Folder or file where RAG system is defined
Notes
Ensure that the uploaded PDF is properly formatted for accurate text extraction.
This app uses Flask sessions for storing user data such as the uploaded file.
For production use, ensure that the SECRET_KEY is more secure than the default ('12345').
License
This project is licensed under the MIT License.

vbnet
Copy
Edit

### How to Use:
1. Replace `<repository_url>` with your actual GitHub repository URL where others can clone it.
2. You can now copy and paste this entire content directly into the `README.md` file in your GitHub repository.
