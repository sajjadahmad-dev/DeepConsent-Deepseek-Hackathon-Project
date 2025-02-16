import os
import streamlit as st
from openai import OpenAI
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Set up DeepSeek API
API_KEY = os.getenv("API_KEY")
base_url = "https://api.aimlapi.com/v1"
client = OpenAI(api_key=API_KEY, base_url=base_url)

# Streamlit UI Setup
st.set_page_config(page_title="🔐 AI-Powered Smart Consent System", layout="centered")
st.title("🔐 AI-Powered Smart Consent System")
st.write("Generate, analyze, and gain insights on consent agreements with DeepSeek AI.")

# Sidebar Settings
with st.sidebar:
    st.header("⚙ Settings")
    language = st.selectbox("Select Language", ["English", "Spanish", "French", "German", "Chinese"])
    compliance = st.selectbox("Ensure Compliance With", ["GDPR", "HIPAA", "CCPA", "None"])
    template = st.selectbox("Choose Template", ["Medical Research", "Data Sharing", "Legal Agreement", "Custom"])

# Store history in session state
if "history" not in st.session_state:
    st.session_state.history = []

# Function to Save as PDF
def save_as_pdf(text, filename="output.pdf"):
    pdf_filename = f"{filename}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    
    y_position = 750  # Start position
    for line in text.split("\n"):
        c.drawString(100, y_position, line[:90])  # Limit line width
        y_position -= 20  # Move down for next line
    
    c.save()
    return pdf_filename

# Tabs
tab1, tab2 = st.tabs(["Generate Consent", "Analyze Document"])

# Generate Consent Agreement
with tab1:
    st.header("Generate Consent Agreement")
    user_prompt = st.text_area("Enter your request:", "Generate a consent agreement for medical research.")
    
    if st.button("Generate Consent Agreement"):
        with st.spinner("Generating..."):
            try:
                completion = client.chat.completions.create(
                    model="deepseek/deepseek-r1",
                    messages=[
                        {"role": "system", "content": f"You are a legal AI assistant. Generate a consent agreement in {language}, ensuring compliance with {compliance}."},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.7,
                    max_tokens=1024,
                )
                response = completion.choices[0].message.content
                st.success("✅ Consent Agreement Generated Successfully!")
                st.text_area("AI-Generated Consent Agreement:", response, height=300)

                # Store in history
                st.session_state.history.append({"timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "response": response})

                # Download buttons
                st.download_button("Download as Text", data=response, file_name="consent_agreement.txt", mime="text/plain")
                
                # PDF Download
                pdf_file = save_as_pdf(response, "consent_agreement")
                with open(pdf_file, "rb") as file:
                    st.download_button("Download as PDF", data=file, file_name="consent_agreement.pdf", mime="application/pdf")

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Analyze Document
with tab2:
    st.header("Analyze Document")
    uploaded_file = st.file_uploader("Upload a consent document (PDF or text)", type=["pdf", "txt"])

    if uploaded_file is not None:
        extracted_text = uploaded_file.read().decode("utf-8")
        st.text_area("Extracted Text:", extracted_text, height=200)

        if st.button("Analyze Document"):
            with st.spinner("Analyzing..."):
                try:
                    analysis_prompt = f"""
                    Analyze the following document and provide:
                    1. A summary of the document.
                    2. Key legal risks and compliance issues.
                    3. Recommendations for improvements.
                    Document:
                    {extracted_text}
                    """
                    completion = client.chat.completions.create(
                        model="deepseek/deepseek-chat",
                        messages=[
                            {"role": "system", "content": "You are an AI-powered document analysis assistant."},
                            {"role": "user", "content": analysis_prompt},
                        ],
                        temperature=0.7,
                        max_tokens=1024,
                    )
                    analysis_response = completion.choices[0].message.content
                    st.success("✅ Document Analysis Complete!")
                    st.text_area("Analysis Results:", analysis_response, height=300)

                    # Store in history
                    st.session_state.history.append({"timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "response": analysis_response})

                    # Download options
                    st.download_button("Download Analysis as Text", data=analysis_response, file_name="document_analysis.txt", mime="text/plain")

                    # PDF Download
                    pdf_file = save_as_pdf(analysis_response, "document_analysis")
                    with open(pdf_file, "rb") as file:
                        st.download_button("Download Analysis as PDF", data=file, file_name="document_analysis.pdf", mime="application/pdf")

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

        # DeepSeek Insights Feature
        if st.button("DeepSeek Insights"):
            with st.spinner("Generating Insights..."):
                try:
                    insights_prompt = f"""
                    Explain this document in simple terms for someone unfamiliar with legal language.
                    Provide an easy-to-understand summary and its key implications.
                    Document:
                    {extracted_text}
                    """
                    completion = client.chat.completions.create(
                        model="deepseek/deepseek-r1",
                        messages=[
                            {"role": "system", "content": "You are an AI assistant simplifying legal documents."},
                            {"role": "user", "content": insights_prompt},
                        ],
                        temperature=0.7,
                        max_tokens=1024,
                    )
                    insights_response = completion.choices[0].message.content
                    st.success("✅ Insights Generated!")
                    st.text_area("DeepSeek Insights:", insights_response, height=300)

                    # Store in history
                    st.session_state.history.append({"timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "response": insights_response})

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# Display History
st.header("📜 History")
if st.session_state.history:
    for entry in st.session_state.history:
        with st.expander(f"Response Generated on {entry['timestamp']}"):
            st.text_area("Generated Text:", entry['response'], height=150)
else:
    st.write("No agreements or analyses generated yet.")

# Footer
st.markdown("---")
st.markdown("*Developed by Sajjad Ahmad* | Powered by DeepSeek AI")
