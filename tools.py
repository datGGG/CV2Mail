import io
import os

import docx
import pypdf
import pytesseract
from PIL import Image
import openai
import google.generativeai as genai


class CV_text_extractor:
    
    def __init__(self): 
        pass

    def extract_text_from_pdf(self,file_path):
        """Extracts text from a PDF file."""
        text = ""
        try:
            with open(file_path, "rb") as file:
                reader = pypdf.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() or ""  # Handle None returns
        except Exception as e:
            print(f"Error processing PDF: {e}")
        return text

    def extract_text_from_doc(self,file_path):
        """Extracts text from a .doc file (using antiword)."""
        try:
            import subprocess

            process = subprocess.Popen(
                ["antiword", file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()
            return stdout.decode("utf-8", errors="ignore")  # Handle potential encoding issues.
        except ImportError:
            print("antiword is not installed. Please install it to process .doc files.")
            return ""
        except FileNotFoundError:
            print("antiword not found. Please ensure it's in your system's PATH.")
            return ""
        except Exception as e:
            print(f"Error processing DOC: {e}")
            return ""


    def extract_text_from_docx(self,file_path):
        """Extracts text from a .docx file."""
        text = ""
        try:
            doc = docx.Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            print(f"Error processing DOCX: {e}")
        return text

    def extract_text_from_image_pdf(self,file_path):
        """Extracts text from a PDF of images (using OCR)."""
        try:
          text = ""
          with open(file_path, "rb") as file:
              reader = pypdf.PdfReader(file)
              for page_num in range(len(reader.pages)):
                  page = reader.pages[page_num]
                  for image in page.images:
                      with Image.open(io.BytesIO(image.data)) as img:
                          text += pytesseract.image_to_string(img) + "\n"
          return text
        except ImportError:
            print("Pillow, pytesseract, or pypdf not installed. Install them to process image PDFs.")
            return ""
        except Exception as e:
            print(f"Error processing image PDF: {e}")
            return ""


    def convert_file_to_text(self,file_path):
        """Converts a file to text based on its extension."""
        _, extension = os.path.splitext(file_path)
        extension = extension.lower()

        if extension == ".pdf":
            text = self.extract_text_from_pdf(file_path)
            if not text.strip(): #if no text was extracted, it might be an image pdf.
              text = self.extract_text_from_image_pdf(file_path)
            return text
        elif extension == ".doc":
            return self.extract_text_from_doc(file_path)
        elif extension == ".docx":
            return self.extract_text_from_docx(file_path)
        else:
            return "Unsupported file format."

    def save_text_to_file(self,text, output_file_path="C:\hoc hoc hoc\HK7\CV_to_Email\output.txt"):
        """Saves the extracted text to a .txt file."""
        try:
            with open(output_file_path, "w", encoding="utf-8") as output_file:
                output_file.write(text)
            print(f"Text saved to {output_file_path}")
        except Exception as e:
            print(f"Error saving text to file: {e}")
        

class Txt_summarizer:
    def __init__(self,api_key):
        self.api_key=api_key
        self.cache ={}
        
    def summarize_resume_with_gpt3(self,resume_text, api_key):
        """
        Summarizes a resume using the GPT-3.5 Turbo API.

        Args:
            resume_text: The text content of the resume.
            api_key: Your OpenAI API key.

        Returns:
            A string containing the summarized resume, or None if an error occurred.
        """

        openai.api_key = api_key

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": f"Summarize the following resume, including the name, experience, and key highlights:\n\n{resume_text}"
                    }
                ],
                max_tokens=500,  # Adjust as needed
            )
            return response.choices[0].message["content"].strip()
        except openai.error.OpenAIError as e:
            print(f"Error calling OpenAI API: {e}")
            return None
        except KeyError:
            print("Error: unexpected response from OpenAI API.")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None


    def summarize_resume_with_gemini(self,resume_text, api_key):
        """
        Summarizes a resume using the Gemini API.

        Args:
            resume_text: The text content of the resume.
            api_key: Your Gemini API key.

        Returns:
            A string containing the summarized resume, or None if an error occurred.
        """
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash')  

            prompt = f"""Summarize the following resume, then extract these information:
            - name
            - job position
            - skills
            - experience
            - year of experience
            - education
            - location
            \n\n{resume_text}"""
            response = model.generate_content(prompt)
            return response.text.strip() 

        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return None


    def process_resume(self,resume_file_path, api_key,model="Gemini", output_file_path="resume_summary.txt"):
        """
        Processes a resume file, summarizes it using Gemini, and saves the summary.

        Args:
            resume_file_path: The path to the resume file (PDF, DOC, DOCX).
            api_key: Your Gemini API key.
            output_file_path: The path to save the summary.
        """
        extractor= CV_text_extractor()
        resume_text = extractor.convert_file_to_text(file_path=resume_file_path)

        if not resume_text:
            print("Could not extract text from the resume.")
            return 
        if resume_text in self.cache:
            print("Retrieving summary from cache.")
            return self.cache[resume_text]
        summary = self.summarize_resume_with_gemini(resume_text, api_key)
        self.cache[resume_text] = summary
        # summary = self.summarize_resume_with_gpt3(resume_text, api_key)
        if summary:
            tmp = CV_text_extractor()
            tmp.save_text_to_file(summary, output_file_path)
            return summary
        return 

class Email_generator:
    def __init__(self,tone,previous_email):
        self.tone = tone
        self.previous_email = previous_email
      
    def generate_email_with_gemini(self, summarized_resume=None, api_key=None):
        """
        Generates an email using the Gemini API, incorporating tone and style from previous emails.

        Args:
            prompt: The main prompt for the email content.
            tone: Desired tone of the email (e.g., formal, informal, enthusiastic).
            previous_email: A previous email to extract writing style from.
            api_key: Your Gemini API key.

        Returns:
            The generated email text, or None if an error occurs.
        """

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')

        full_prompt = f"You are a recruiter consultant, from a summarize resume,\
            you need no write an email to the recruit manager about the candidate. \
            Here is the candidate's resume:\n\n{summarized_resume}"
        print(full_prompt)
        if self.tone:
            full_prompt += f"\n\nWrite in a {self.tone} tone."

        if self.previous_email:
            full_prompt += f"\n\nUse the writing style from the following email:\n\n{self.previous_email}"

        try:
            
            response = model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            print(f"Error generating email: {e}")
            return None
        
    def save_generated_output(self,summarized_resume=None, filepath="email.txt",api_key=None):
        email = self.generate_email_with_gemini(summarized_resume=summarized_resume,api_key=api_key)
        saver = CV_text_extractor()
        saver.save_text_to_file(email,filepath)