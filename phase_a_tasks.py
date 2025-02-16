import os
import json
import imghdr
import glob
import sqlite3
import pytesseract
from PIL import Image
import numpy as np
  # Importing OCR library
from datetime import datetime
from flask import jsonify
from dateutil import parser
from utils import run_command, call_openai_api

def get_day_number(target):
    target = target.lower()  # Normalize input for consistency
    d = -1  # Default value in case of an invalid day

    if target == "monday" or target == "mondays":
        d = 0
    elif target == "tuesday" or target == "tuesdays":
        d = 1
    elif target == "wednesday" or target == "wednesdays":
        d = 2
    elif target == "thursday" or target == "thursdays":  # Fixed typo: "thrusday" → "thursday"
        d = 3
    elif target == "friday" or target == "fridays":
        d = 4
    elif target == "saturday" or target == "saturdays":  # Fixed typo: "sundays" → "saturdays"
        d = 5
    elif target == "sunday" or target == "sundays":
        d = 6

    return d
def get_most_similar_comments(comments, embeddings):
    embeddings = np.array([emb["embedding"] for emb in embeddings])
    similarity = np.dot(embeddings, embeddings.T)

    # Ignore self-similarity by setting diagonal to -inf
    np.fill_diagonal(similarity, -np.inf)

    # Get indices of most similar comments
    i, j = np.unravel_index(similarity.argmax(), similarity.shape)
    expected = "\n".join(sorted([comments[i], comments[j]]))

    return expected


def a1(require, url):
    response, error, code = run_command(f"pip install {require}")
    if code != 0:
        return jsonify({"error": error}), 500

    response, error, code = run_command(f"uv run {url} {os.environ.get('USER_EMAIL')}")
    if code != 0:
        return jsonify({"error": error}), 500

    return jsonify({"message": "Task A1 completed successfully"}), 200


def a2(input_file, output_file, require):
    response, error, code = run_command(f"npm install {require}")
    if code != 0:
        return jsonify({"error": error}), 500

    response, error, code = run_command(f"npx prettier --write {input_file}")
    if code != 0:
        return jsonify({"error": error}), 500

    return jsonify({"message": "Task A2 completed successfully"}), 200


def a3(input_file, output_file, target):
    with open(input_file) as file:
        dates = file.readlines()

    
    wednesdays = sum(1 for date in dates if parser.parse(date.strip()).weekday() == get_day_number(target))

    with open(output_file, 'w') as file:
        file.write(str(wednesdays))

    return jsonify({"message": "Task A3 completed successfully"}), 200


def a4(input_file, output_file):
    with open(input_file) as file:
        contacts = json.load(file)

    sorted_contacts = sorted(contacts, key=lambda x: (x['last_name'], x['first_name']))

    with open(output_file, 'w') as file:
        json.dump(sorted_contacts, file, indent=2)

    return jsonify({"message": "Task A4 completed successfully"}), 200


def a5(input_file, output_file):
    logs = sorted(glob.glob(input_file), key=os.path.getmtime, reverse=True)[:10]

    with open(output_file, 'w') as outfile:
        for log in logs:
            with open(log) as infile:
                outfile.write(infile.readline())

    return jsonify({"message": "Task A5 completed successfully"}), 200


def a6(input_file, output_file):
    index = {}

    for filepath in glob.glob(input_file, recursive=True):
        with open(filepath) as file:
            for line in file:
                if line.startswith('# '):
                    index[os.path.relpath(filepath, '/data/docs/')] = line[2:].strip()
                    break
        with open(output_file, 'w') as file:
            json.dump(index, file, indent=2)

    return jsonify({"message": "Task A6 completed successfully"}), 200


def a7(input_file, output_file, prompt):
    with open(input_file) as file:
        email_content = file.read()

    response = call_openai_api("chat/completions", {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": f"{prompt}: {email_content}"}]
    })

    if "choices" in response and response["choices"]:
        email_address = response["choices"][0]["message"]["content"].strip()
    else:
        return jsonify({"error": "Failed to extract email"}), 500

    with open(output_file, 'w') as file:
        file.write(email_address)

    return jsonify({"message": "Task A7 completed successfully"}), 200

def a8(input_file, output_file, prompt):
    # Read and encode the image in base64
    with open(input_file, "rb") as image_file:
        image_data = image_file.read()
        image_base64 = base64.b64encode(image_data).decode("utf-8")

    # Detect the actual image format
    image_format = imghdr.what(input_file)  # More reliable than splitting the filename
    if image_format not in ["png", "jpeg", "jpg"]:
        return jsonify({"error": f"Unsupported image format: {image_format}"}), 400

    mime_type = f"image/{image_format}"  # Ensures correct MIME type

    # OpenAI API Request
    response = call_openai_api("chat/completions", {
        "model": "gpt-4o-mini",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{image_base64}"
                    }
                }
            ]
        }]
    })

    # Process the response
    if response and "choices" in response and response["choices"]:
        extracted_text = response["choices"][0]["message"]["content"].strip()
    else:
        return jsonify({"error": "Failed to extract credit card number"}), 500

    # Save extracted text
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(extracted_text)

    return jsonify({"message": "Task A8 completed successfully"}), 200


def a9(input_file, output_file):
    with open(input_file) as file:
        comments = file.readlines()

    response = call_openai_api("embeddings", {
        "model": "text-embedding-3-small",
        "input": comments
    })

    if "data" in response:
        embeddings = response["data"]
        similar_pair = get_most_similar_comments(comments, embeddings)
    else:
        return jsonify({"error": "Failed to get embeddings"}), 500

    with open(output_file, 'w') as file:
        file.write(similar_pair)

    return jsonify({"message": "Task A9 completed successfully"}), 200


def a10(input_file, output_file, query):
    try:
        conn = sqlite3.connect(input_file)
        cursor = conn.cursor()
        cursor.execute(query)
        total_sales = cursor.fetchone()[0]
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

    with open(output_file, 'w') as file:
        file.write(str(total_sales))

    return jsonify({"message": "Task A10 completed successfully"}), 200
