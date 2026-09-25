import streamlit as st
import google.generativeai as genai
import PyPDF2

# Design the webpage header
st.title("Upload Your Resume")
st.write("Get a chance to see which jobs you qualify for in India and what skills you need to learn.")

# File uploader widget
uploaded_file = st.file_uploader("Upload your Resume (PDF format)", type="pdf")

if uploaded_file is not None:
    if st.button("Analyze My Resume with AI"):
        st.info("🧠 AI is reading your resume... Please wait a few seconds.")
        
        try:
            # 1. Read the PDF file
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            resume_text = ""
            for page in pdf_reader.pages:
                resume_text += page.extract_text()
            
            # 2. Connect to Gemini securely
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            # 3. Give Gemini your specific Indian Job Market instructions
            prompt = """
            You are an expert Indian Career Counselor. Analyze this resume text. 
            Evaluate based on Indian qualification standards (e.g., B.Tech, BCA, B.Com, MBA).
            Provide exactly this structure:
            1. Match Score (0-100%)
            2. Top 3 Job Roles in India right now
            3. Skill Gaps (3 specific tools missing)
            4. Learning Roadmap (Specific free resources to bridge the gap)
            """
            
            # 4. Get the AI scorecard
            response = model.generate_content(prompt + "\n\nResume Text: " + resume_text)
            
            # 5. Show it on screen
            st.success("✅ Analysis Complete!")
            st.markdown(response.text)
            
        except Exception as e:
           st.error(f"System Error: {e}")
