import os
from typing import List
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# Force absolute path lookup for the .env file
base_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(base_dir, '.env')
load_dotenv(dotenv_path=dotenv_path)

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY is empty or missing in tailor_engine.py!")

# 1. Define the tailored output schema using Pydantic
class TailoredSuggestions(BaseModel):
    tailored_summary: str = Field(description="A powerful, 3-line professional summary tailored specifically to align with the target JD's key requirements.")
    bullet_point_optimizations: List[str] = Field(description="Action-oriented, metrics-driven bullet points rewritten from the candidate's existing experience to better highlight relevant impact or bridge skill gaps.")
    suggested_skills_to_add: List[str] = Field(description="A list of highly relevant keywords or tools from the JD that the candidate should add to their skills section if they possess basic familiarity.")

# 2. Initialize the LLM
llm = ChatGroq(
    temperature=0.3,  # Low temperature for contextual accuracy, a tiny bit of creative phrasing for resume impact
    model_name="llama-3.3-70b-versatile",
    api_key=api_key
)

def tailor_resume_profile(parsed_profile_json: str, job_description_text: str) -> TailoredSuggestions:
    """Generates targeted resume optimizations to align a candidate's profile with a specific job description."""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are an expert executive resume writer and career coach. "
            "Your objective is to help the candidate optimize their resume for a target job description. "
            "Review their current profile and the target JD. Provide actionable, high-impact resume modifications "
            "including a specialized professional summary and tailored accomplishment bullet points. "
            "Ensure the tone remains professional, confident, and metrics-driven, without inventing false credentials."
        )),
        ("human", (
            "### Candidate Parsed Profile JSON:\n{profile_json}\n\n"
            "### Target Job Description:\n{job_description}\n\n"
            "Generate the tailored optimization suggestions matching the requested schema."
        ))
    ])
    
    # Bind the structured schema
    structured_llm = llm.with_structured_output(TailoredSuggestions)
    tailor_chain = prompt | structured_llm
    
    # Execute the chain
    suggestions = tailor_chain.invoke({
        "profile_json": parsed_profile_json,
        "job_description": job_description_text
    })
    
    return suggestions

# --- Local Testing Block ---
if __name__ == "__main__":
    # Simulating your profile structure
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
    
    # Target Job Description
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
    
    print("Generating tailored resume suggestions...")
    try:
        tailored_output = tailor_resume_profile(sample_profile_json, sample_jd)
        print("\n--- Resume Optimizations Generated Successfully! ---")
        print(tailored_output.model_dump_json(indent=2))
    except Exception as e:
        print(f"An error occurred during tailoring: {e}")