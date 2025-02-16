import os
import subprocess
import requests
import json  # Import JSON module
import re,json


def run_command(command):
    """Executes a shell command and returns stdout, stderr, and exit code."""
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE, text=True)
    return result.stdout, result.stderr, result.returncode

def call_openai_api(endpoint, payload):
    """Calls OpenAI API via AIProxy and returns the response JSON."""
    AIPROXY_TOKEN = os.environ.get("AIPROXY_TOKEN")
    if not AIPROXY_TOKEN:
        raise ValueError("Error: AIPROXY_TOKEN is not set in environment variables.")

    HEADERS = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AIPROXY_TOKEN}"
    }
    url = f"https://aiproxy.sanand.workers.dev/openai/v1/{endpoint}"
    
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        return response.json()  # Return as JSON object
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {e}"}

def classify_task(task_description):
    """Analyzes a task description and extracts structured details as a JSON object."""
    
    prompt = (
        f"""
        Task: Analyze the given task description and extract structured details in JSON format. Ensure that fields are accurately populated and never mixed across different tasks.
         Your goal is to determine the correct action based on predefined categories while ensuring accuracy, consistency, and completeness
         predifined categoeies(script,format,count,sort,extract,index,parse,recognize,match,compute,fetch,commit,query,scrape,compress,transcribe,convert,filter)
        ⚠️ Important Notes:

        - please read task description very carefully generate the best json data 
        - If task_description is given in any language, always respond in English.
        - Never mix fields from different tasks; ensure each JSON response is isolated.
        - Always extract file paths exactly as provided.
        - If a task mentions multiple operations, break it down only if they require separate steps.
        - If a query/task is repeated, do not change its input path; always use the original.
        - If a field is not applicable, return `null`.

        ### 🛠 RULES FOR TASK CLASSIFICATION:
        - If the task is **equivalent to an existing known task (A1-B10)**, use the **exact same action name** as the reference task.
        - Do not invent new action names—always align with existing tasks if possible.
        - Ensure consistency across different languages and phrasings.

        🎯 **Extract the following fields in valid JSON format:**
        ```json
        {{
            "action": "Primary operation to perform (generate,format,count,sort,extract,index,parse,recognize,match,compute,fetch,commit,query,scrape,compress,transcribe,convert,filter)",
            "target": "The object being acted upon (e.g., Wednesdays, comments, emails, image)",
            "input_file": "File(s) used in the operation (if applicable)",
            "output_file": "File where the result should be stored (if applicable)",
            "width": "New width for resizing an image (if provided, else null)",
            "height": "New height for resizing an image (if provided, else null)",
            "quality": "Quality (1-100) for resizing/compressing images (default to 85 if unspecified)",
            "query": "SQL query for database operations",
            "prompt": "Formatted prompt if task requires LLM processing",
            "url": "Any extracted URL (e.g., API endpoint, GitHub repo, website)",
            "require": "Dependencies required (e.g., pillow for images, flask for APIs, whisper for transcription)",
            "api_method": "API request method (GET, POST, etc.) if applicable",
            "filters": "Conditions when filtering data (e.g., from CSV or API)",
            "commit_message": "Commit message when modifying a Git repo (if mentioned)",
            "language": "Programming language when dealing with code/scripts (e.g., Python, SQL, JavaScript)",
            "date_format": "Date format if parsing dates (e.g., YYYY-MM-DD)"
        }}
        ```
        ## **🔹 TASK EXAMPLES:**
        
        ### **A1. Generate Data Files**
        **Task:** Install `uv` (if required) and run "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py" with email as the only argument.
        ```json
        {{
            "action": "generate",
            "target": "data files",
            "input_file": "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py",
            "output_file": null,
            "width": null 
            "height": null 
            "quality": null
            "query": null
            "prompt": null 
            "url": null 
            "require": ["uv"],
            "api_method": null
            "filters": null 
            "commit_message": null 
            "language": null 
            "date_format": null 
        }}
        ```

        ### **A3. Count Specific Days in a List**
        **Task:** "The file `/data/dates.txt` contains a list of dates, one per line. Count the number of Wednesdays in the list, and write just the number to `/data/dates-wednesdays.txt`"
        ```json
        {{
            "action": "count",
            "target": "Wednesdays",
            "input_file": "/data/dates.txt",
            "output_file": "/data/dates-wednesdays.txt",
            "width": null 
            "height": null 
            "quality": null
            "query": null,
            "prompt": null
            "url": null 
            "require": null 
            "api_method": null
            "filters": null 
            "commit_message": null 
            "language": null 
            "date_format": null 
        }}
        ```

        ### **A5. Extract the First Line of Recent Logs**
        **Task:** "Write the first line of the 10 most recent `.log` file in `/data/logs/` to `/data/logs-recent.txt`, most recent first".
        ```json
        {{
            "action": "extract",
            "target": "first line of recent logs",
            "input_file": "/data/logs/*.log",
            "output_file": "/data/logs-recent.txt",
            "prompt": null
            "width": null 
            "height": null 
            "quality": null
            "query": null,
            "url": null 
            "require": null 
            "api_method": null
            "filters": null 
            "commit_message": null 
            "language": null 
            "date_format": null 
        }}
        ```
                ### **A6. Extract the First Line of Recent Logs**
        **Task:** "Find all Markdown (`.md`) files in `/data/docs/`.for each file, extract the first occurrance of each H1 (i.e. a line starting with `# `).
                  Create an index file `/data/docs/index.json` that maps each filename (without the `/data/docs/` prefix) to its title
                  (e.g. "README.md": "Home", "path/to/large-language-models.md": "Large Language Models", ...)".
        ```json
        {{
            "action": "index",
            "target": "rewrite",
            "input_file": "/data/docs/**/*md",
            "output_file": "/data/docs/index.json",
            "prompt": null
            "width": null 
            "height": null 
            "quality": null
            "query": null,
            "url": null 
            "require": null 
            "api_method": null
            "filters": null 
            "commit_message": null 
            "language": null 
            "date_format": null 
        }}
        ```






        ### **A7. Extract the First Line of Recent Logs**
        **Task:**  "`/data/email.txt` contains an email message. Pass the content to an LLM with instructions to extract the sender's email address, and write just the email address to `/data/email-sender.txt.
        ```json
        {{
            "action": "parse",
            "target": "email - extraction",
            "input_file": "/data/email.txt",
            "output_file": "/data/email-sender.txt",
            "prompt":Pass the content to an LLM with instructions to extract the sender's email address, and write just the email address 
            "width": null 
            "height": null 
            "quality": null
            "query": null,
            "url": null 
            "require": null 
            "api_method": null
            "filters": null 
            "commit_message": null 
            "language": null 
            "date_format": null 
        }}
        ```

        ### **A10. Compute Total Sales for "Gold" Tickets**
        **Task:**'The SQLite database file `/data/ticket-sales.db` has a `tickets` with columns `type`, `units`, and `price`. Each row is a customer bid for a concert ticket. What is the total sales of all the items in the "Gold" ticket type? Write the number in `/data/ticket-sales-gold.txt`'
        ```json
        {{
            "action": "query",
            "target": "total sales",
            "input_file": "/data/ticket-sales.db",
            "output_file": "/data/ticket-sales-gold.txt",
            "width": null 
            "height": null 
            "quality": null
            "query": "SELECT SUM(units * price) FROM tickets WHERE type = 'Gold'",
            "prompt": null
            "url": null 
            "require": null 
            "api_method": null
            "filters": null 
            "commit_message": null 
            "language": null 
            "date_format": null 
        }}
        ```

        ### **B3. Fetch API Data**
        **Task:** Fetch JSON data from `https://api.example.com/data` and save it to `/data/api-data.json`.
        ```json
        {{
            "action": "fetch",
            "target": "API data",
            "input_file": null,
            "output_file": "/data/api-data.json",
            "width": null 
            "height": null 
            "quality": null
            "query": null
            "prompt": null 
            "url": "https://api.example.com/data",
            "require": null 
            "api_method": "GET",
            "query": null,
             "filters": null 
            "commit_message": null 
            "language": null 
            "date_format": null 

        }}
        ```

        ### **B5. Run SQL Query on SQLite**
        **Task:** Get the top 5 products from `/data/products.db`.
        ```json
        {{
            "action": "query",
            "target": "top 5 products",
            "input_file": "/data/products.db",
            "width": null 
            "height": null 
            "quality": null
            "output_file": null,
            "query": "SELECT * FROM products ORDER BY sales DESC LIMIT 5",
            "prompt": null
            "url": null 
            "require": null 
            "api_method": null
            "filters": null 
            "commit_message": null 
            "language": null 
            "date_format": null 
        }}
        ```

        ### **B6. Scrape Data from a Website**
        **Task:** Extract the top 10 trending articles from `https://news.example.com` and save to `/data/news.json`.
        ```json
        {{
            "action": "scrape",
            "target": "trending articles",
            "input_file": null,
            "output_file": "/data/news.json",
            "width": null 
            "height": null 
            "quality": null
            "query": null
            "prompt": null 
            "url": "https://news.example.com",
            "require": null 
            "api_method": null
            "filters": null 
            "commit_message": null 
            "language": null 
            "date_format": null 
        }}
        ```

        ### **B8. Transcribe an Audio File**
        **Task:** Transcribe `/data/interview.mp3` and save it to `/data/interview.txt`.
        ```json
        {{
            "action": "transcribe",
            "target": "speech to text",
            "input_file": "/data/interview.mp3",
            "output_file": "/data/interview.txt",
            "width": null 
            "height": null 
            "quality": null
            "query": null
            "prompt": null 
            "url": null 
            "require": ["whisper"],
            "api_method": null
            "filters": null 
            "commit_message": null 
            "language": null 
            "date_format": null 
        }}
        ```


        📝 Task Description:
        {task_description}
        """
    )

    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}]
    }
    
    response = call_openai_api("chat/completions", payload)

    if "choices" in response and response["choices"]:
        json_response = response["choices"][0]["message"]["content"].strip()

    # ✅ Remove triple backticks if present
        json_cleaned = re.sub(r"```json\s*|\s*```", "", json_response, flags=re.DOTALL).strip()

        try:
            return json.loads(json_cleaned)  # Parse the cleaned JSON
        except json.JSONDecodeError:
            print("JSON Parse Error: Response was not valid JSON.")
            return {"error": "Failed to parse response as JSON.", "raw_response": json_cleaned}
