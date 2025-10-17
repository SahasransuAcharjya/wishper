from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import requests

app = Flask(__name__)
app.secret_key = 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIB8E098aefk8rHg4VfwhD2UBdN0qBBv/Pqp4ay6zZ7fa'  # Session secret key for Flask sessions

# Dummy users for login validation
DUMMY_USERS = {
    "user1": "password123",
    "admin": "adminpass"
}

# Your unique Ollama API key
OLLAMA_API_KEY = "872c59aaa9dc4d009397e659dc5f677a.5UfVaeVvVl1Gtb3ct1cpIW5v"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in DUMMY_USERS and DUMMY_USERS[username] == password:
            session['username'] = username
            return redirect(url_for('chat'))
        else:
            error = 'Invalid username or password'
            return render_template('login.html', error=error)
    else:
        return render_template('login.html')

@app.route('/chat')
def chat():
    if not session.get('username'):
        return redirect(url_for('login'))
    return render_template('chat.html', username=session['username'])

@app.route('/chat', methods=['POST'])
def chat_post():
    if not session.get('username'):
        return jsonify({"error": "Not logged in"}), 401

    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        headers = {
            "Authorization": f"Bearer {OLLAMA_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "mistral",
            "prompt": user_message,
            "max_tokens": 100
            # Add other parameters if needed
        }
        response = requests.post(
            "https://api.ollama.com/v1/generate",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        data = response.json()
        bot_reply = data.get('response', 'Sorry, no reply from Ollama.')

        return jsonify({"reply": bot_reply})

    except requests.exceptions.RequestException as e:
        print("Error calling Ollama API:", e)
        return jsonify({"reply": "Sorry, the chatbot is temporarily unavailable."})

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
