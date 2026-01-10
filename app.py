import os
import time
import random
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

client = OpenAI()

# Use threading mode to avoid async issues
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise Exception("❌ OPENAI_API_KEY is missing in environment variables")
client = OpenAI(api_key=api_key)

@app.route('/')
def index():
    return render_template("index.html")

@socketio.on('user_message')
def handle_user_message(data):
    user_message = data.get('message', '').strip()
    if not user_message:
        return

    emit('ai_typing')
    time.sleep(random.uniform(0.5, 1.0))

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=500,
            temperature=0.7
        )
        ai_text = response.choices[0].message.content.strip()
        emit('ai_response', {'response': ai_text})
    except Exception as e:
        emit('ai_response', {'response': f"Error: {e}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    socketio.run(app, host="127.0.0.1", port=port, debug=False)

