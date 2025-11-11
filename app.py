from flask import Flask, request, render_template_string, jsonify

app = Flask(__name__)

html = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Role-based Creative Chatbot</title>
<style>
body {font-family: Arial; background:#f4f4f4; margin:0; padding:0;}
.container {width:80%; max-width:800px; margin:40px auto; background:white; border-radius:10px; box-shadow:0 0 10px rgba(0,0,0,0.1); padding:20px;}
select, input, button {padding:10px; margin:5px; border-radius:6px; border:1px solid #ccc;}
button {background:#007bff; color:white; cursor:pointer;}
button:hover {background:#0056b3;}
.message {margin:10px 0;}
.user {color:#007bff; font-weight:bold;}
.bot {color:#333;}
</style>
</head>
<body>
<div class="container">
  <h2>🎭 Role-based Creative Chatbot</h2>
  <div>
    <label>Choose Role:</label>
    <select id="role">
      <option>Storyteller</option>
      <option>Philosopher</option>
      <option>Comedian</option>
      <option>Coach</option>
      <option>Poet</option>
      <option>Game Designer</option>
      <option>Marketing Expert</option>
      <option>Scientist</option>
    </select>
    <label>Creativity:</label>
    <select id="creativity">
      <option>Low</option>
      <option selected>Medium</option>
      <option>High</option>
    </select>
  </div>
  <input type="text" id="msg" placeholder="Type your message..." style="width:70%;">
  <button onclick="send()">Send</button>
  <div id="chat"></div>
</div>

<script>
async function send() {
  const msg = document.getElementById("msg").value;
  const role = document.getElementById("role").value;
  const creativity = document.getElementById("creativity").value;
  if (!msg.trim()) return;
  const chat = document.getElementById("chat");
  chat.innerHTML += `<div class='message'><span class='user'>You:</span> ${msg}</div>`;
  document.getElementById("msg").value = '';
  const res = await fetch('/chat', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({msg, role, creativity})
  });
  const data = await res.json();
  chat.innerHTML += `<div class='message'><span class='bot'>${role}:</span> ${data.reply}</div>`;
  chat.scrollTop = chat.scrollHeight;
}
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(html)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    msg = data.get("msg","")
    role = data.get("role","Storyteller")
    creativity = data.get("creativity","Medium")

    responses = {
        "Storyteller": f"As a storyteller, let me spin a tale about '{msg}'.",
        "Philosopher": f"As a philosopher, I reflect deeply: '{msg}' reveals truth beyond words.",
        "Comedian": f"Haha! '{msg}' sounds like my last punchline!",
        "Coach": f"You can do it! '{msg}' is just the start of greatness.",
        "Poet": f"In gentle verses, '{msg}' blooms like dawn upon dreams.",
        "Game Designer": f"Let's design a hero whose quest starts with '{msg}'.",
        "Marketing Expert": f"'{msg}' could be the perfect campaign tagline!",
        "Scientist": f"Analyzing '{msg}'... fascinating data indeed."
    }
    extra = {"Low": " (Simple style)", "Medium": " (Balanced tone)", "High": " (Unleashing full creativity!)"}
    reply = responses.get(role, "Let's chat!") + extra.get(creativity, "")
    return jsonify({"reply": reply})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
