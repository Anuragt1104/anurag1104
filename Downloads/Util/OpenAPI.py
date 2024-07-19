import json
import requests

from flask import Flask, request, jsonify

app = Flask(__name__)

api_key = "YOUR_OPENAI_API_KEY"

@app.route("/complete", methods=["POST"])
def complete_prompt():
    try:
        prompt = request.json.get("prompt")
        if not prompt:
            return "Invalid request. 'prompt' is missing in the request body.", 400

        url = "https://api.openai.com/v1/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        data = {
            "prompt": prompt,
            "model": "text-davinci-003",
            "temperature": 0,
            "max_tokens": 2000
        }

        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            response_data = response.json()
            choices = response_data.get("choices")
            if choices and len(choices) > 0:
                choice = choices[0]
                text = choice.get("text", "")
                text = text.replace("JSON Output:", "").split("~~~~", 1)[-1].strip()
                return text
            else:
                return "No completion choice available in the response."
        else:
            return f"Request failed with status: {response.status_code}", 500

    except Exception as e:
        return f"An error occurred: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)