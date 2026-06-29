💼 CareerCopilot AI

An AI-powered career copilot that parses your resume, scores it against any job description, rewrites it for the role, and generates outreach messages — all in one Streamlit app.

Built to solve a real problem: tailoring a resume and outreach for every job application is repetitive and slow. CareerCopilot AI automates the first pass so you can apply faster, with sharper, role-specific positioning.


What it does

CareerCopilot AI runs on four LLM-powered engines, each producing structured, validated output (via Pydantic) rather than raw, unreliable text:

EngineWhat it doesResume Parser (parser_service.py)Extracts structured candidate data — skills, education, experience - from an uploaded PDF resume using pdfplumber + an LLM call, validated into a typed schemaJob Match Engine (match_engine.py)Scores the parsed profile against a pasted job description, returning an overall match %, technical skill score, experience alignment score, key strengths, and missing critical skillsResume Tailoring Engine (tailor_engine.py)Generates a role-specific professional summary, optimized bullet points, and high-value keywords to add, based on the match analysisOutreach Generator (outreach_generator.py)Produces a LinkedIn connection message, a cold referral email, and a follow-up sequence tailored to the specific company and role

All four engines are orchestrated through a single Streamlit interface with persistent session state, so a user can upload once and move through profile review → match scoring → tailoring → outreach without re-entering data.


Tech Stack


Frontend/App: Streamlit
LLM Orchestration: LangChain (langchain-core, langchain-groq) calling Groq-hosted models
Data Validation: Pydantic - every LLM response is parsed into a typed schema before being shown to the user, preventing malformed output from breaking the UI
PDF Parsing: pdfplumber
Persistence: SQLite (user profile + session state across tabs)
Config: python-dotenv for API key management



Why Pydantic matters here

LLM outputs are unstructured by default. Every engine in this app defines a strict Pydantic schema for its expected output (e.g. overall_match_percentage, strengths, missing_critical_skills), so the LLM's response is validated and type-checked before it ever reaches the UI. This eliminates the runtime crashes that come from assuming an LLM will always return clean, well-formed data.


Run it locally

bashgit clone https://github.com/manasvimittal27/CareerCopilot-AI.git
cd CareerCopilot-AI
pip install -r requirements.txt

Create a .env file with your Groq API key:

GROQ_API_KEY=your_key_here

Then run:

bashstreamlit run app.py


Project Structure

CareerCopilot-AI/
├── app.py                   # Streamlit UI + tab orchestration
├── parser_service.py        # Resume parsing engine
├── match_engine.py          # Job-match scoring engine
├── tailor_engine.py         # Resume tailoring engine
├── outreach_generator.py    # Outreach message generator
├── database.py               # SQLite schema + session/user state
├── requirements.txt
└── .gitignore


Roadmap


 Add a vector-based semantic match (beyond keyword/LLM scoring) for more robust job-fit comparisons
 Multi-resume version tracking per user
 Export tailored resume directly to PDF/DOCX


Author
Manasvi Mittal 
