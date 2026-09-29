import streamlit as st
import google.generativeai as genai
import PyPDF2
import docx

# Design the webpage header
st.title("Upload Your Resume")
st.write("Get a chance to see which jobs you qualify for in India and what skills you need to learn.")

# File uploader widget
uploaded_file = st.file_uploader("Upload your Resume (PDF format or Word format)", type=["pdf" , "docx"])

if uploaded_file is not None:
    if st.button("Analyze My Resume with AI"):
        
        try:
            st.info("⏳ Step 1: Extracting text from your file...")
            
            # 1. Read PDF or Word document text
            resume_text = ""
            if uploaded_file.name.endswith(".pdf"):
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                for page in pdf_reader.pages:
                    extracted_text = page.extract_text()
                    if extracted_text:
                        resume_text += extracted_text
            elif uploaded_file.name.endswith(".docx"):
                doc = docx.Document(uploaded_file)
                resume_text = "\n".join([p.text for p in doc.paragraphs if p.text])
            
            st.info("✅ Step 2: Text extracted! Connecting to Google Gemini...")
            
            # 2. Connect to Gemini securely
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel("gemini-3.8-flash")
            
            # 3. Give Gemini your specific Indian Job Market instructions
            prompt = """
            You are an expert Indian Career Counselor. Analyze this resume text. 
            Evaluate based on all Indian qualification standards (e.g., B.Tech, BCA, B.Com, MBA).
            Provide exactly this structure:
            1. Match Score (0-100%)
            2. Top 5 Job Roles in India right now
            3. Skill Gaps (3 specific tools missing for each)
            4. Learning Roadmap (describe the skills missing and how can one learn, also if needed provide the user with the free resources available in the internet across all platforms for the user to get a user-friendly suggesstions)
            """
            
            st.info("🧠 Step 3: AI is analyzing (this takes 5-15 seconds)...")
            
            # 4. Get the AI scorecard WITH A TIMEOUT
            response = model.generate_content(
                prompt + "\n\nResume Text: " + resume_text,
                request_options={"timeout": 90}
            )
            
            # 5. Show it on screen
            st.success("✅ Analysis Complete!")
            st.markdown(response.text)
            
        except Exception as e:
            st.error(f"System Error: {e}")
