from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# --- HTML Template ---
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Role-based Creative Chatbot</title>
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            background: #f8fafc;
            margin: 0;
            padding: 0;
        }
        .chat-container {
            width: 70%;
            margin: 40px auto;
            background: #fff;
            border-radius: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 25px;
        }
        h1 {
            text-align: center;
            color: #2b2b2b;
        }
        .config {
            margin-bottom: 20px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            justify-content: space-between;
        }
        select, input, button {
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #ccc;
            font-size: 15px;
        }
        button {
            background-color: #007bff;
            color: white;
            border: none;
            cursor: pointer;
        }
        button:hover {
            background-color: #0056b3;
        }
        .messages {
            border-top: 1px solid #ddd;
            margin-top: 20px;
            padding-top: 15px;
            height: 400px;
            overflow-y: auto;
        }
        .message {
            margin-bottom: 12px;
        }
        .user {
            color: #007bff;
            font-weight: bold;
        }
        .bot {
            color: #333;
        }
    </style>
</head>
<body>
<div class="chat-container">
    <h1>🎭 Role-based Creative Chatbot</h1>
    <div class="config">
        <label>
            Choose a Role:
            <select id="role">
                <option>Storyteller</option>
                <option>Philosopher</option>
                <option>Stand-up Comedian</option>
                <option>Motivational Coach</option>
                <option>Game Character Designer</option>
                <option>Poet</option>
                <option>Marketing Strategist</option>
                <option>AI Scientist</option>
            </select>
        </label>
        <label>
            Creativity:
            <select id="creativity">
                <option value="Low">Low</option>
                <option value="Medium" selected>Medium</option>
                <option value="High">High</option>
            </select>
        </label>
        <label>
            Tone:
            <select id="tone">
                <option>Professional</option>
                <option>Friendly</option>
                <option>Humorous</option>
                <option>Inspirational</option>
                <option>Mysterious</option>
            </select>
        </label>
        <label>
            Language:
            <select id="language">
                <option>English</option>
                <option>Spanish</option>
                <option>French</option>
                <option>Chinese</option>
                <option>Japanese</option>
            </select>
        </label>
    </div>
    <div>
        <input type="text" id="user_input" placeholder="Type your message..." style="width:80%;">
        <button onclick="sendMessage()">Send</button>
    </div>
    <div class="messages" id="chat_box"></div>
</div>

<script>
async function sendMessage() {
    const input = document.getElementById("user_input").value;
    const role = document.getElementById("role").value;
    const creativity = document.getElementById("creativity").value;
    const tone = document.getElementById("tone").value;
    const language = document.getElementById("language").value;

    if (!input.trim()) return;

    const chatBox = document.getElementById("chat_box");
    chatBox.innerHTML += `<div class='message'><span class='user'>You:</span> ${input}</div>`;
    document.getElementById("user_input").value = "";

    const res = await fetch("/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({input, role, creativity, tone, language})
    });
    const data = await res.json();
    chatBox.innerHTML += `<div class='message'><span class='bot'>${role} Bot:</span> ${data.reply}</div>`;
    chatBox.scrollTop = chatBox.scrollHeight;
}
</script>
</body>
</html>
"""

# --- Backend logic ---
@app.route("/")
def index():
    return render_template_string(html_template)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("input", "")
    role = data.get("role", "Storyteller")
    creativity = data.get("creativity", "Medium")
    tone = data.get("tone", "Professional")
    language = data.get("language", "English")

    # Simple AI response simulation logic
    base_responses = {
        "Storyteller": f"As a storyteller, let me weave a tale around '{user_input}'...",
        "Philosopher": f"As a philosopher, I ponder your question deeply: '{user_input}'. The essence lies within reflection.",
        "Stand-up Comedian": f"Haha! You said '{user_input}' — that’s funnier than my last joke night!",
        "Motivational Coach": f"Believe in yourself! '{user_input}' is just the first step toward greatness!",
        "Game Character Designer": f"Let's craft a character based on '{user_input}' — with bold traits and a mysterious past.",
        "Poet": f"In whispers and verse, '{user_input}' blooms into emotion untold.",
        "Marketing Strategist": f"To market '{user_input}', we need a creative hook and emotional connection.",
        "AI Scientist": f"Analyzing '{user_input}' through a neural network of possibilities..."
    }

    creativity_boost = {
        "Low": " (keeping ideas simple and grounded.)",
        "Medium": " (adding a touch of imagination.)",
        "High": " (unleashing wild creativity!)"
    }

    tone_mods = {
        "Professional": " I’ll keep this formal and informative.",
        "Friendly": " Let’s chat casually, like good friends!",
        "Humorous": " Expect some witty sparks here!",
        "Inspirational": " Let’s make it uplifting and motivational!",
        "Mysterious": " I’ll wrap it in enigma and intrigue..."
    }

    response = base_responses.get(role, "Let's talk!") + creativity_boost.get(creativity, "") + tone_mods.get(tone, "")
    reply = f"[{language}] {response}"

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
