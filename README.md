# CV2Mail
use LLM to summarize CV and write Email for recruiter
## How to use
1. Setup environment variables (.env file)
    GOOGLE_API_KEY ="your api key"
    OPENAI_API_KEY=" your api key"
    SUPABASE_URL="your supabase url"
    SUPABASE_KEY="your supabase key"
    CV_FROM_USER="save directory for uploaded files"
2. Install required libraries: 
```bash
pip install requirement.txt
```
3. Run application
```bash
streamlit run app.py
```
4. (Optional) Test model output (e.g CV_summarization, Email generation)
```bash 
python test.py
```