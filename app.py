import os
from flask import Flask, request, jsonify
from phase_a_tasks import (
    a1, a2, a3, a4, a5, a6, a7, a8, a9, a10
)
from phase_b_tasks import (
    b3, b4, b5, b6, b7, b8, b9, b10
)
from utils import classify_task

app = Flask(__name__)

@app.route('/run', methods=['POST'])
def run_task():
    task = request.args.get('task')
    if not task:
        return jsonify({"error": "No task provided"}), 400

    classification = classify_task(task)
    print(classification)
    # Safely extract values with defaults
    action = classification.get("action", "").lower()
    target = classification.get("target", "").lower()
    input_file = classification.get("input_file", "")
    output_file = classification.get("output_file", "")
    width = classification.get("width",100)
    height = classification.get("height",100)
    quality = classification.get("quality", 85)  # Default quality is 85
    query = classification.get("query")
    prompt = classification.get("prompt")
    url = classification.get("url")
    require = classification.get("require", [])
    api_method = classification.get("api_method", "")
    filters = classification.get("filters")
    commit_message = classification.get("commit_message", "")
    language = classification.get("language", "")
    date_format = classification.get("date_format", "")

    # Phase A Tasks
    if action == "generate":
        return a1(require[0], url)
    elif action == "format" and target == "markdown file":
        return a2(input_file, output_file, require[0])
    elif action == "count":
        return a3(input_file, output_file, target)
    elif action == "sort":
        return a4(input_file, output_file)
    elif action == "extract":
        return a5(input_file, output_file)
    elif action == "index":
        return a6(input_file, output_file)
    elif action == "parse":
        return a7(input_file, output_file, prompt)
    elif action == "recognize":
        return a8(input_file, output_file, prompt)
    elif action == "match":
        return a9(input_file, output_file)
    elif action == "query":
        return a10(input_file, output_file, query)

    # Phase B Tasks
    elif action == "fetch" :
        return b3(url, output_file, api_method, filters)
    elif action == "clone" :
        return b4(url, commit_message)
    elif action == "compute":
        return b5(input_file, output_file, query)
    elif action == "scrape" :
        return b6(url, output_file)
    elif action == "compress" :
        return b7(input_file, output_file, width, height, quality, require)
    elif action == "transcribe" :
        return b8(input_file, output_file, require)
    elif action == "convert" :
        return b9(input_file, output_file)
    elif action == "filter": 
        return b10(input_file, output_file, filters, language)

    return jsonify({"error": "Task not recognized"}), 400

@app.route('/read', methods=['GET'])
def read_file():
    path = request.args.get('path')
    if not os.path.exists(path):
        return "", 404
    abs_path = os.path.realpath(path)
    
    # Ensure it is within /data
    if not abs_path.startswith(os.path.realpath('/data')):
        return "You are not authorized to use this space", 404

        
    with open(path, 'r') as file:
        content = file.read()
    return content, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8000)
