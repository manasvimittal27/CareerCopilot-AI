import os
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
    raise ValueError("GROQ_API_KEY is empty or missing in outreach_generator.py!")

# 1. Define the outreach communication suite schema using Pydantic
class OutreachSuite(BaseModel):
    linkedin_message: str = Field(description="A high-impact, professional LinkedIn message strictly under 300 characters for connection requests.")
    referral_email: str = Field(description="A structured email draft to an employee or alumnus asking for a referral, highlighting relevant overlapping background.")
    follow_up_sequence: str = Field(description="A concise, polite 2-sentence follow-up message to send 4-5 days later if there is no response.")

# 2. Initialize the LLM
llm = ChatGroq(
    temperature=0.7,  # Higher temperature for natural, charismatic, and persuasive professional writing
    model_name="llama-3.3-70b-versatile",
    api_key=api_key
)

def generate_outreach_suite(parsed_profile_json: str, job_description_text: str, company_name: str) -> OutreachSuite:
    """Generates a contextual networking communication suite for LinkedIn and email outreach."""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are an expert executive networking coach and career strategist. "
            "Your objective is to generate hyper-personalized, high-conversion networking assets "
            "for the candidate based on their profile, target role, and the company. "
            "Avoid generic buzzwords or corporate fluff. Write communications that sound authentic, "
            "highly respectful of the recipient's time, and subtly highlight why the candidate's "
            "background makes them an excellent fit for the team. Keep the tone warm yet strictly professional."
        )),
        ("human", (
            "### Target Company Name:\n{company_name}\n\n"
            "### Candidate Parsed Profile JSON:\n{profile_json}\n\n"
            "### Target Job Description:\n{job_description}\n\n"
            "Generate the full Outreach Suite matching the requested schema. "
            "Ensure the LinkedIn message is brief enough to fit character limits safely."
        ))
    ])
    
    # Bind the structured schema
    structured_llm = llm.with_structured_output(OutreachSuite)
    outreach_chain = prompt | structured_llm
    
    # Execute the chain
    communication_suite = outreach_chain.invoke({
        "company_name": company_name,
        "profile_json": parsed_profile_json,
        "job_description": job_description_text
    })
    
    return communication_suite

# --- Local Testing Block ---
if __name__ == "__main__":
    sample_company = "Meesho"
    
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
    
    sample_jd = """
    We are looking for an AI & Data Engineer to join our growing product team. 
    
    Responsibilities:
    - Build LLM-powered backend orchestration tools and agent workflows.
    - Leverage FastAPI to build highly async APIs.
    - Manage complex querying using SQL and build operational dashboards in Tableau.
    """
    
    print(f"Generating custom outreach sequence for {sample_company}...")
    try:
        outreach_output = generate_outreach_suite(sample_profile_json, sample_jd, sample_company)
        print("\n--- Outreach Suite Generated Successfully! ---")
        print(outreach_output.model_dump_json(indent=2))
    except Exception as e:
        print(f"An error occurred during outreach generation: {e}")