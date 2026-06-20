import os
from typing import List
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# Force absolute path lookup for the .env file (reusing our bulletproof fix)
base_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(base_dir, '.env')
load_dotenv(dotenv_path=dotenv_path)

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY is empty or missing in match_engine.py!")

# 1. Define the premium structured scorecard using Pydantic
class MatchScorecard(BaseModel):
    overall_match_percentage: int = Field(description="An integer from 0 to 100 representing the overall job fit.")
    technical_skills_score: int = Field(description="An integer from 0 to 100 assessing alignment of hard skills/tools.")
    experience_alignment_score: int = Field(description="An integer from 0 to 100 assessing domain, responsibility, and scope match.")
    strengths: List[str] = Field(description="Top 2-4 major strengths where the candidate excels relative to the JD.")
    missing_critical_skills: List[str] = Field(description="Key skills, technologies, or tools explicitly mentioned in the JD that are missing from the resume.")
    short_summary: str = Field(description="A brief, 2-sentence candid assessment of why the candidate does or doesn't fit the role.")

# 2. Initialize the Groq LLM using the working llama-3.3 model
llm = ChatGroq(
    temperature=0.2,  # Low temperature for analytical precision
    model_name="llama-3.3-70b-versatile",
    api_key=api_key
)

def evaluate_job_match(parsed_profile_json: str, job_description_text: str) -> MatchScorecard:
    """Compares a parsed resume profile against a job description text and returns a structured evaluation."""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are an elite corporate technical recruiter and talent scout. "
            "Your task is to stringently evaluate the candidate's parsed resume details "
            "against the provided Job Description (JD). Be entirely realistic and honest — "
            "do not over-inflate scores. Calculate scores analytically based on the direct alignment "
            "of skills, scope of experience, and role requirements."
        )),
        ("human", (
            "### Candidate Parsed Profile JSON:\n{profile_json}\n\n"
            "### Target Job Description:\n{job_description}\n\n"
            "Generate the comprehensive Match Scorecard matching the requested schema."
        ))
    ])
    
    # Bind the structured schema
    structured_llm = llm.with_structured_output(MatchScorecard)
    match_chain = prompt | structured_llm
    
    # Execute the chain
    scorecard = match_chain.invoke({
        "profile_json": parsed_profile_json,
        "job_description": job_description_text
    })
    
    return scorecard

# --- Local Testing Block ---
if __name__ == "__main__":
    # Mock data modeling what your parser generated
    sample_profile_json = """
    {
      "name": "Manasvi",
      "email": "manasvi@example.com",
      "skills": ["Python", "LangChain", "Data Analysis", "FastAPI", "Machine Learning", "Operations Tracking"],
      "experience": [
        "Senior Associate at Meesho - managed data projects to optimize delivery partner allocation and tracked supplier update loops.",
        "Organized and managed high-traffic infrastructure stalls for regional community initiatives."
      ],
      "education": [
        "B.Sc. in Computer Science, Mathematics, and Physics - St. Stephen's College"
      ]
    }
    """
    
    # A challenging sample Job Description to test gaps
    sample_jd = """
    We are looking for an AI & Data Engineer to join our growing product team. 
    
    Responsibilities:
    - Build LLM-powered backend orchestration tools and agent workflows.
    - Leverage FastAPI to build highly async APIs.
    - Manage complex querying using SQL and build operational dashboards in Tableau.
    
    Requirements:
    - Proficient in Python and core generative AI frameworks like LangChain or LangGraph.
    - Strong database skills (SQL is a must).
    - Experience in e-commerce operational tracking or marketplace logistics is a major plus.
    - Experience with visualization tools like Tableau or PowerBI.
    """
    
    print("Evaluating job fit against the description...")
    try:
        evaluation = evaluate_job_match(sample_profile_json, sample_jd)
        print("\n--- Match Scorecard Generated Successfully! ---")
        print(evaluation.model_dump_json(indent=2))
    except Exception as e:
        print(f"An error occurred during evaluation: {e}")