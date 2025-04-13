from utils import *
import os
import io
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    file_path = input("Enter the path to your file: ")  # Get file path from user.
    api_key = os.getenv("GOOGLE_API_KEY")
    # api_key = os.getenv("OPENAI_API_KEY")
    if os.path.exists(file_path):
        tone = "formal and professional"
        previous_mail= None
        txt_extractor = CV_text_extractor()
        
        text = txt_extractor.convert_file_to_text(file_path)
        txt_extractor.save_text_to_file(text)
        
        summarizer =Txt_summarizer(api_key=api_key)
        sumarized_CV = summarizer.process_resume(file_path, api_key)
        generator = Email_generator(tone=tone,previous_email=previous_mail)
        generator.save_generated_output(sumarized_CV,api_key=api_key)
    else:
        print("File not found.")
    
    