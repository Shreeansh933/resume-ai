import streamlit as st
import google.generativeai as genai
import PyPDF2
import docx

# Page configuration
st.set_page_config(page_title="AI Resume Analyzer", layout="centered")
st.title("Upload Your Resume")
st.write("Get a chance to see which jobs you qualify for in India and what skills you need to learn.")

# File uploader widget (PDF and Word)
uploaded_file = st.file_uploader(
    "Upload your Resume (PDF format or Word format)", 
    type=["pdf", "docx"]
)

if uploaded_file is not None:
    if st.button("Analyze My Resume with AI"):
        try:
            # 1. Read document text based on file extension
            with st.spinner("Extracting text from resume..."):
                resume_text = ""
                if uploaded_file.name.endswith(".pdf"):
                    pdf_reader = PyPDF2.PdfReader(uploaded_file)
                    for page in pdf_reader.pages:
                        extracted = page.extract_text()
                        if extracted:
                            resume_text += extracted + "\n"
                elif uploaded_file.name.endswith(".docx"):
                    doc = docx.Document(uploaded_file)
                    resume_text = "\n".join([p.text for p in doc.paragraphs if p.text])

            if not resume_text.strip():
                st.error("No readable text found. Please ensure the document is not an image-only scan.")
                st.stop()

            # 2. Configure Gemini API
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

            # 4. Stream the generation to prevent 504 Gateway / Deadline timeouts
            st.info("🧠 AI is analyzing your resume...")

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

            # Generator function to stream tokens chunk-by-chunk in real time
            def stream_data():
                for chunk in response:
                    if chunk.text:
                        yield chunk.text

            st.success("✅ Analysis Complete!")
            st.write_stream(stream_data())

        except Exception as e:
            st.error(f"System Error: {e}")
