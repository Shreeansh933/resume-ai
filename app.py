import streamlit as st
import google.generativeai as genai
import PyPDF2
import docx

# Design the webpage header
st.set_page_config(page_title="AI Resume Analyzer", layout="centered")
st.title("Upload Your Resume")
st.write("Get a chance to see which jobs you qualify for in India and what skills you need to learn.")

# File uploader widget
uploaded_file = st.file_uploader(
    "Upload your Resume (PDF format or Word format)", 
    type=["pdf", "docx"]
)

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
                        resume_text += extracted_text + "\n"
            elif uploaded_file.name.endswith(".docx"):
                doc = docx.Document(uploaded_file)
                resume_text = "\n".join([p.text for p in doc.paragraphs if p.text])

            if not resume_text.strip():
                st.error("The uploaded file does not contain readable text. If it is an image scan, please use an editable document.")
                st.stop()

            st.info("✅ Step 2: Text extracted! Connecting to Google Gemini...")
            
            # 2. Connect to Gemini securely
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel("gemini-3.8-flash")
            
            # 3. Targeted prompt for Indian employment landscape
            prompt = f"""
            You are an expert Indian Career Counselor. Analyze this resume text against current job market trends in India. 
            Evaluate based on all Indian qualification standards (e.g., B.Tech, BCA, B.Com, MBA).
            
            Provide exactly this structure:
            1. Match Score (0-100%)
            2. Top 5 Job Roles in India right now
            3. Skill Gaps (3 specific tools missing for each)
            4. Learning Roadmap (describe the skills missing and how can one learn, providing free resources available across the internet for user-friendly suggestions).

            Resume Text:
            {resume_text}
            """
            
            st.info("🧠 Step 3: AI is analyzing (streaming output)...")
            
            # 4. Stream content with generation limits and 90s timeout to prevent 504 errors
            generation_config = genai.GenerationConfig(
                temperature=0.2,
                max_output_tokens=1500
            )
            
            response = model.generate_content(
                prompt,
                generation_config=generation_config,
                stream=True,
                request_options={"timeout": 90}
            )
            
            # Stream generator function to display text progressively
            def stream_data():
                for chunk in response:
                    if chunk.text:
                        yield chunk.text

            # 5. Display output dynamically
            st.success("✅ Analysis Complete!")
            st.write_stream(stream_data())
            
        except Exception as e:
            st.error(f"System Error: {e}")
