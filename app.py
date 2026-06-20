import streamlit as st
import json
import os

# Import the core engines you built this week
from parser_service import parse_resume
from match_engine import evaluate_job_match
from tailor_engine import tailor_resume_profile
from outreach_generator import generate_outreach_suite

# Set page configuration
st.set_page_config(
    page_title="CareerCopilot AI",
    page_icon="💼",
    layout="wide"
)

st.title("💼 CareerCopilot AI")
st.caption("Your autonomous career advisor powered by LangChain & Groq")
st.markdown("---")

# Initialize session state variables so data persists across clicks
if "parsed_profile" not in st.session_state:
    st.session_state.parsed_profile = None

# --- SIDEBAR: INPUT CONTROL ---
with st.sidebar:
    st.header("📄 Input Artifacts")
    
    # 1. Resume Upload
    uploaded_file = st.file_uploader("Upload your Resume (PDF)", type=["pdf"])
    
    if uploaded_file is not None:
        # Temporarily save file locally for your parser to read
        with open("temp_uploaded_resume.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        if st.button("⚡ Parse & Analyze Resume"):
            with st.spinner("ATS Parser extracting structured profile..."):
                try:
                    profile = parse_resume("temp_uploaded_resume.pdf")
                    st.session_state.parsed_profile = json.loads(profile.model_dump_json())
                    st.success("Resume parsed successfully!")
                except Exception as e:
                    st.error(f"Parsing failed: {e}")
                    
    # Clean up local file if it exists
    if os.path.exists("temp_uploaded_resume.pdf"):
        os.remove("temp_uploaded_resume.pdf")

    st.markdown("---")
    
    # 2. Target Job Details
    st.header("🏢 Target Job Details")
    company_name = st.text_input("Company Name", placeholder="e.g. OpenAI")
    job_description = st.text_area("Job Description (Paste Text)", height=250, placeholder="Paste the complete requirements...")

# --- MAIN DASHBOARD INTERFACE ---
if st.session_state.parsed_profile is None:
    st.info("👋 Welcome! Please upload and parse your resume in the left sidebar to begin.")
else:
    # Display brief welcome with user name if extracted
    candidate_name = st.session_state.parsed_profile.get('name', 'Candidate')
    st.success(f"Active Profile Loaded: **{candidate_name}** ({st.session_state.parsed_profile.get('email', '')})")
    
    # Set up interactive operational tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Profile Overview", 
        "🎯 Job Match Analysis", 
        "📝 Resume Tailoring", 
        "✉️ Outreach Strategy"
    ])
    
    # TAB 1: SHOW PARSED RESUME PROFILE
    with tab1:
        st.subheader("Extracted Professional Profile")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 💪 Skills Extracted")
            st.json(st.session_state.parsed_profile.get("skills", []))
            
            st.markdown("#### 🎓 Education")
            st.json(st.session_state.parsed_profile.get("education", []))
        with col2:
            st.markdown("#### 💼 Experience Records")
            st.json(st.session_state.parsed_profile.get("experience", []))
            
    # TAB 2: JOB MATCH ENGINE
    with tab2:
        st.subheader("Recruiter Alignment Scorecard")
        if not job_description:
            st.warning("Please paste a target Job Description in the sidebar to run the evaluation.")
        else:
            if st.button("📈 Calculate Job Match Fit"):
                with st.spinner("Analyzing skill matrices and alignment scores..."):
                    try:
                        # Convert profile dict back to JSON string for the engine
                        profile_str = json.dumps(st.session_state.parsed_profile)
                        scorecard = evaluate_job_match(profile_str, job_description)
                        
                        # Display Premium Score KPI blocks
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Overall Match Fit", f"{scorecard.overall_match_percentage}%")
                        c2.metric("Technical Skill Score", f"{scorecard.technical_skills_score}%")
                        c3.metric("Experience Alignment", f"{scorecard.experience_alignment_score}%")
                        
                        st.markdown(f"> **Recruiter Assessment Summary:** {scorecard.short_summary}")
                        
                        col_left, col_right = st.columns(2)
                        with col_left:
                            st.success("### Major Highlighted Strengths")
                            for strength in scorecard.strengths:
                                st.markdown(f"* {strength}")
                        with col_right:
                            st.error("### Missing Critical Skills/Gaps")
                            for gap in scorecard.missing_critical_skills:
                                st.markdown(f"* {gap}")
                                
                    except Exception as e:
                        st.error(f"Evaluation pipeline failed: {e}")

    # TAB 3: RESUME TAILORING SUGGESTIONS
    with tab3:
        st.subheader("Targeted Resume Modification Suite")
        if not job_description:
            st.warning("Please paste a target Job Description in the sidebar to generate optimizations.")
        else:
            if st.button("🔧 Generate Custom Optimizations"):
                with st.spinner("Rewriting experience vectors for alignment..."):
                    try:
                        profile_str = json.dumps(st.session_state.parsed_profile)
                        tailored_data = tailor_resume_profile(profile_str, job_description)
                        
                        st.markdown("### 🎯 Recommended Professional Summary")
                        st.info(tailored_data.tailored_summary)
                        
                        st.markdown("### 📈 Optimized Accomplishment Bullet Points")
                        for bp in tailored_data.bullet_point_optimizations:
                            st.markdown(f"✅ {bp}")
                            
                        st.markdown("### 🛠️ High-Value Keywords to Embed")
                        st.write(", ".join([f"`{skill}`" for skill in tailored_data.suggested_skills_to_add]))
                        
                    except Exception as e:
                        st.error(f"Tailoring system failed: {e}")

    # TAB 4: OUTREACH GENERATOR
    with tab4:
        st.subheader("Networking & Referral Sequence Builder")
        if not job_description or not company_name:
            st.warning("Please provide both a Company Name and Job Description in the sidebar to script outreach assets.")
        else:
            if st.button("🚀 Compose Conversion Outreach Suite"):
                with st.spinner("Generating custom social scripts..."):
                    try:
                        profile_str = json.dumps(st.session_state.parsed_profile)
                        outreach = generate_outreach_suite(profile_str, job_description, company_name)
                        
                        st.markdown("### 💬 LinkedIn Connection Request (Under 300 Chars)")
                        st.code(outreach.linkedin_message, language="text")
                        
                        st.markdown("### ✉️ Cold Referral Request Email")
                        st.code(outreach.referral_email, language="text")
                        
                        st.markdown("### 🕒 High-Conversion Follow-up Sequence")
                        st.code(outreach.follow_up_sequence, language="text")
                        
                    except Exception as e:
                        st.error(f"Outreach composition failed: {e}")