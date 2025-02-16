import os
import json
import pandas as pd
import requests
import sqlite3
from flask import jsonify
from utils import run_command, call_openai_api


def b3(url, output_file, api_method="GET", filters=None):
    try:
        response = requests.request(api_method, url)
        response.raise_for_status()
        data = response.json()

        if filters:
            data = {k: v for k, v in data.items() if k in filters}

        with open(output_file, 'w') as file:
            json.dump(data, file, indent=2)

        return jsonify({"message": "Task B3 completed successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def b4(url, commit_message="Updated repository"):
    try:
        response, error, code = run_command(f"git clone {url} /data/repo")
        if code != 0:
            return jsonify({"error": error}), 500

        response, error, code = run_command(
            f"cd /data/repo && touch new_file.txt && git add new_file.txt && git commit -m '{commit_message}' && git push"
        )
        if code != 0:
            return jsonify({"error": error}), 500

        return jsonify({"message": "Task B4 completed successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def b5(input_file, output_file, query):
    try:
        conn = sqlite3.connect(input_file)
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()[0]
        conn.close()

        with open(output_file, 'w') as file:
            json.dump(results, file, indent=2)

        return jsonify({"message": "Task B5 completed successfully"}), 200
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500


def b6(url, output_file):
    try:
        response = requests.get(url)
        response.raise_for_status()

        with open(output_file, 'w') as file:
            file.write(response.text)

        return jsonify({"message": "Task B6 completed successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def b7(input_file, output_file, width, height, quality, require="resize"):
    try:
        resize_option = f"-resize {width}x{height}"
        quality_option = f"-quality {quality}"

        response, error, code = run_command(f"convert {input_file} {resize_option} {quality_option} {output_file}")
        if code != 0:
            return jsonify({"error": error}), 500

        return jsonify({"message": "Task B7 completed successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def b8(input_file, output_file, require="transcribe"):
    try:
        response = call_openai_api("chat/completions", {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": f"Transcribe the following audio: {input_file}"}]
        })

        if "choices" in response and response["choices"]:
            transcription = response["choices"][0]["message"]["content"].strip()
        else:
            return jsonify({"error": "Failed to extract transcription"}), 500

        with open(output_file, 'w') as file:
            file.write(transcription)

        return jsonify({"message": "Task B8 completed successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def b9(input_file, output_file):
    try:
        response, error, code = run_command(f"pandoc {input_file} -o {output_file}")
        if code != 0:
            return jsonify({"error": error}), 500

        return jsonify({"message": "Task B9 completed successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def b10(input_file, output_file, filters=None, language="python"):
    try:
        df = pd.read_csv(input_file)

        if filters:
            df = df.query(filters)

        df.to_json(output_file, orient='records', indent=2)

        return jsonify({"message": f"Task B10 completed successfully in {language}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
