import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
from tools import *
import os
import base64


load_dotenv()
api_key=os.getenv("GOOGLE_API_KEY")
upload_cv=os.getenv("CV_FROM_USER")
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)


def download_text(text, filename="downloaded_text.txt"):
    """Creates a download link for the given text."""
    b64 = base64.b64encode(text.encode()).decode() 
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">Download text file</a>'
    return href

def sign_up(email, password):
    try:
        user = supabase.auth.sign_up({"email": email, "password": password})
        return user
    except Exception as e:
        st.error(f"Registration failed: {e}")

def sign_in(email, password):
    try:
        user = supabase.auth.sign_in_with_password({"email": email, "password": password})
        return user
    except Exception as e:
        st.error(f"Login failed: {e}")

def sign_out():
    try:
        supabase.auth.sign_out()
        st.session_state.user_email = None
        st.rerun()
    except Exception as e:
        st.error(f"Logout failed: {e}")
def text_editor(text=None):
    """Implements a simple text editor using Streamlit."""

    st.title("Simple Text Editor")

    # Initialize session state for text content if it doesn't exist
    if "text_content" not in st.session_state:
        st.session_state.text_content = "implement"

    text_input = st.text_area("Enter your text:", value=st.session_state.text_content, height=300)

    if st.button("Save Changes"):
        st.session_state.text_content = text_input
        st.success("Changes saved!")

    st.write("Preview:")
    st.write(st.session_state.text_content)

    if st.button("Clear"):
      st.session_state.text_content = ""
      st.rerun()
def process_audio_user(uploaded_files):
    if not uploaded_files:
        return
    if not os.path.exists(upload_cv):
        os.makedirs(upload_cv)
        print("Created audio_from_user folder")
    st.write("File uploaded:", uploaded_files.name)
    # Save file to audio_from_user folder
    with open(os.path.join(upload_cv, uploaded_files.name), "wb") as f:
        f.write(uploaded_files.getbuffer())
    file_dir = os.path.join(upload_cv, uploaded_files.name)
    return file_dir
    
def main_app(user_email):
    
    st.title("🎉 Welcome Page")
    st.success(f"Welcome, {user_email}! 👋")
    if st.button("Logout"):
        sign_out()
    st.header("Import your CV here!")
    uploaded_file = st.file_uploader("Upload PDF, DOCX, or DOC files", type=["pdf", "docx", "doc"], accept_multiple_files=False)
    tone = st.selectbox(
    "Which tone would you like to use?",
    ("Formal and Professional",
     "Friendly and Approachable",
     "Assertive and Confident",
     "Warm and Conversational",
     "Short and Punchy"),
    placeholder="Select writing tone")
    previous_mail =""
    initial_text =""
    if uploaded_file:
        file_dir=process_audio_user(uploaded_file)
        txt_extractor = CV_text_extractor()
            
        text = txt_extractor.convert_file_to_text(file_dir)
        txt_extractor.save_text_to_file(text)
        
        summarizer =Txt_summarizer(api_key=api_key)
        sumarized_CV = summarizer.process_resume(file_dir, api_key)
        generator = Email_generator(tone=tone,previous_email=previous_mail)
        email = generator.generate_email_with_gemini(sumarized_CV,api_key=api_key)
        generator.save_generated_output(sumarized_CV,api_key=api_key,response=email)
        initial_text = email
    edited_text = st.text_area("Generated Email:", initial_text, height=200)
    if edited_text:
        st.markdown(download_text(edited_text), unsafe_allow_html=True)

def auth_screen():
    st.title("🔐 Streamlit & Supabase Auth App")
    option = st.selectbox("Choose an action:", ["Login", "Sign Up"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if option == "Sign Up" and st.button("Register"):
        user = sign_up(email, password)
        if user and user.user:
            st.success("Registration successful. Please log in.")

    if option == "Login" and st.button("Login"):
        user = sign_in(email, password)
        if user and user.user:
            st.session_state.user_email = user.user.email
            st.success(f"Welcome back, {email}!")
            st.rerun()

if "user_email" not in st.session_state:
    st.session_state.user_email = None

if st.session_state.user_email:
    main_app(st.session_state.user_email)
    
else:
    auth_screen()
