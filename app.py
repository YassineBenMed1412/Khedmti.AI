import os
from flask import Flask, request, render_template, jsonify
import fitz  
import spacy
import re

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Load Spacy NLP model
nlp = spacy.load("en_core_web_sm")

class ResumeParser:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.text = self.extract_text()

    def extract_text(self):
        """Extracts text from the given PDF file."""
        text = ""
        with fitz.open(self.pdf_path) as doc:
            for page in doc:
                text += page.get_text("text") + "\n"
        return text.strip()

    def extract_entities(self):
        """Uses NLP to extract key entities like Name, Email, Phone, and Skills."""
        doc = nlp(self.text)
        extracted_info = {
            "Name": self.extract_name(doc),
            "Email": self.extract_email(),
            "Phone": self.extract_phone(),
            "Skills": self.extract_skills(doc)
        }
        return extracted_info

    def extract_name(self, doc):
        """Extracts a possible name using Named Entity Recognition (NER)."""
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                return ent.text
        return "Not Found"

    def extract_email(self):
        """Extracts an email using regex."""
        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        match = re.search(email_pattern, self.text)
        return match.group(0) if match else "Not Found"

    def extract_phone(self):
        """Extracts phone number using regex."""
        phone_pattern = r"\(?\+?\d{1,3}\)?[-.\s]?\d{3}[-.\s]?\d{3,4}[-.\s]?\d{3,4}"
        match = re.search(phone_pattern, self.text)
        return match.group(0) if match else "Not Found"

    def extract_skills(self, doc):
        """Extracts skills using simple keyword matching."""
        skills_list = ["Python", "Machine Learning", "Data Science", "NLP", "Java", "SQL", "Flask"]
        extracted_skills = [token.text for token in doc if token.text in skills_list]
        return list(set(extracted_skills)) if extracted_skills else "Not Found"

    def parse(self):
        """Parses the resume and returns extracted information."""
        return {
            "extracted_text": self.text,
            "parsed_data": self.extract_entities()
        }

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"})

    file = request.files["file"]
    
    if file.filename == "":
        return jsonify({"error": "No selected file"})

    if file:
        filepath = os.path.join(app.config[echo "# Khedmti.AI" >> README.md"UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        parser = ResumeParser(filepath)
        extracted_data = parser.parse()

        return jsonify(extracted_data)

if __name__ == "__main__":
    app.run(debug=True)
