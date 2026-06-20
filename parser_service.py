import os
import pdfplumber
from typing import List
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

base_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(base_dir, '.env')
load_dotenv(dotenv_path=dotenv_path)

# Retrieve and check the key immediately
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print(f"\n[DEBUG] Looking for .env at: {dotenv_path}")
    print(f"[DEBUG] Does file exist? {os.path.exists(dotenv_path)}")
    raise ValueError(
        "GROQ_API_KEY is empty or missing! Please open your '.env' file in VS Code "
        "and double-check that it contains exactly: GROQ_API_KEY=gsk_..."
    )

# 1. Define the desired output structure using Pydantic
class StructuredProfile(BaseModel):
    name: str = Field(description="The full name of the candidate")
    email: str = Field(description="The email address of the candidate")
    skills: List[str] = Field(description="List of core technical and soft skills extracted from the resume")
    experience: List[str] = Field(description="List of job titles, companies, and key achievements or responsibilities")
    education: List[str] = Field(description="List of degrees, majors, institutions, and graduation years")

# 2. Initialize the Groq LLM
llm = ChatGroq(
    temperature=0, 
    model_name="llama-3.3-70b-versatile",
    api_key=api_key
)

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts raw text from a PDF file using pdfplumber."""
    raw_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                raw_text += page_text + "\n"
    return raw_text

def parse_resume(pdf_path: str) -> StructuredProfile:
    """Parses raw resume text into a structured Pydantic object."""
    raw_resume_text = extract_text_from_pdf(pdf_path)
    
    if not raw_resume_text.strip():
        raise ValueError("Could not extract any text from the provided PDF.")

    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are an expert ATS (Applicant Tracking System) parser. "
            "Your job is to thoroughly analyze the provided resume text and extract "
            "the candidate's details into the requested structured format. "
            "Do not hallucinate or add outside information."
        )),
        ("human", "Here is the raw resume text:\n\n{resume_text}")
    ])

    # Bind the structured schema to Groq
    structured_llm = llm.with_structured_output(StructuredProfile)
    parser_chain = prompt | structured_llm
    
    # Run the chain
    structured_profile = parser_chain.invoke({"resume_text": raw_resume_text})
    return structured_profile

# --- This block runs automatically when you execute this file ---
if __name__ == "__main__":
    test_pdf = "test_resume.pdf" 
    
    if os.path.exists(test_pdf):
        print(f"Parsing {test_pdf}...")
        try:
            profile = parse_resume(test_pdf)
            print("\n--- Parsing Successful! Here is your structured JSON: ---")
            print(profile.model_dump_json(indent=2))
        except Exception as e:
            print(f"An error occurred: {e}")
    else:
        print(f"\nMissing file: Please drop a sample resume named '{test_pdf}' into this folder to test.")