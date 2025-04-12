import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
# from tools import *
import os
import base64


load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

def download_text(text, filename="downloaded_text.txt"):
    """Creates a download link for the given text."""
    b64 = base64.b64encode(text.encode()).decode()  # Encode to base64
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

def main_app(user_email):
    
    st.title("🎉 Welcome Page")
    st.success(f"Welcome, {user_email}! 👋")
    if st.button("Logout"):
        sign_out()
    st.header("Import your CV here!")
    uploaded_files = st.file_uploader("Upload PDF, DOCX, or DOC files", type=["pdf", "docx", "doc"], accept_multiple_files=False)
    
    option = st.selectbox(
    "Which tone would you like to use?",
    ("Formal and Professional",
     "Friendly and Approachable",
     "Assertive and Confident",
     "Warm and Conversational",
     "Short and Punchy"),
    placeholder="Select writing tone")
    initial_text = "olau"
    edited_text = st.text_area("Edit the text:", initial_text, height=200)
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
