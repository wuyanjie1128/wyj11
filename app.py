from flask import Flask, request, jsonify, render_template_string
import random
import textwrap
import json

app = Flask(__name__)

# ---------------------------
# Role & style configuration
# ---------------------------
ROLES = {
    "Storyteller": {
        "voice": "Warm, vivid, descriptive. Uses narrative arcs and sensory detail.",
        "quirks": [
            "Weave a hook in the opening line.",
            "Add a subtle twist near the end.",
            "Use one metaphor, not more."
        ]
    },
    "Movie Director": {
        "voice": "Cinematic, scene-driven, visual blocking and camera cues.",
        "quirks": [
            "Stage each beat like a shot list.",
            "Include sound design hints.",
            "End with a cut-to-black moment."
        ]
    },
    "Game Master": {
        "voice": "Interactive, second-person, offers choices and consequences.",
        "quirks": [
            "Present at least two branching options.",
            "Describe environment with one tactical detail.",
            "Invite the next action."
        ]
    },
    "UX Copywriter": {
        "voice": "Clear, concise, benefit-first with microcopy polish.",
        "quirks": [
            "Lead with a user benefit.",
            "Use active voice.",
            "End with a crisp CTA."
        ]
    },
    "Debate Coach": {
        "voice": "Structured, steelman opposing views, emphasizes logic and evidence.",
        "quirks": [
            "State thesis in one line.",
            "List strongest counterpoint fairly.",
            "Conclude with action-oriented takeaway."
        ]
    },
    "Travel Planner": {
        "voice": "Friendly, practical, locally-savvy with quick tips.",
        "quirks": [
            "Add time-of-day suggestions.",
            "Note one money-saving tip.",
            "Include a photo-worthy stop."
        ]
    },
    "Poet": {
        "voice": "Rhythmic, image-rich, compact lines.",
        "quirks": [
            "Keep lines under twelve words.",
            "Use one surprising image.",
            "Close with a soft echo."
        ]
    },
    "Comedian": {
        "voice": "Light, observational humor with a gentle punchline.",
        "quirks": [
            "Set up → misdirection → payoff.",
            "One self-aware aside.",
            "Keep it kind, not cruel."
        ]
    }
}

TONES = ["Friendly", "Professional", "Playful", "Dramatic", "Inspiring", "Neutral"]
FORMATS = ["Paragraph", "Bulleted List", "Outline", "Dialogue"]
LENGTHS = {
    "Short": (4, 6),
    "Medium": (7, 11),
    "Long": (12, 18)
}


# ---------------------------
# Helper functions
# ---------------------------
def sentence_split(text):
    parts = [p.strip() for p in text.replace("\n", " ").split(".")]
    return [p for p in parts if p]


def clamp(n, a, b):
    return max(a, min(b, n))


def creative_variations(base, creativity):
    spice_pool = [
        "crisp", "velvet", "luminous", "tactile", "whispering",
        "electric", "quiet", "bold", "nuanced", "sparkling", "grainy", "sleek"
    ]
    k = clamp(int(creativity * 5), 0, 5)
    choices = random.sample(spice_pool, k) if k else []
    if choices:
        base += " " + ", ".join(choices) + "."
    return base


def stylize(text, fmt):
    if fmt == "Paragraph":
        return textwrap.fill(text, width=90)
    if fmt == "Bulleted List":
        parts = sentence_split(text)
        return "\n".join(f"• {p}." for p in parts)
    if fmt == "Outline":
        parts = sentence_split(text)
        return "\n".join(f"{i+1}. {p}." for i, p in enumerate(parts))
    if fmt == "Dialogue":
        parts = sentence_split(text)
        speakers = ["You", "Bot"]
        return "\n".join(f"{speakers[i%2]}: {p}." for i, p in enumerate(parts))
    return text


def apply_constraints(text, extras, fmt):
    if extras.get("no_emojis"):
        text = ''.join(ch for ch in text if ch.isascii())
    if extras.get("force_bullets") and fmt != "Bulleted List":
        lines = sentence_split(text)
        text = "\n".join(f"• {line}" for line in lines)
    if extras.get("quote"):
        text += "\n\n“" + random.choice([
            "Simplicity sharpens ideas.",
            "Contrast creates clarity.",
            "Small steps compound into journeys."
        ]) + "”"
    if extras.get("cta"):
        text += "\n\n→ Try it now and share your next prompt."
    return text


def generate_response(role, tone, user_text, fmt, length_label, creativity, extras):
    role_cfg = ROLES.get(role, ROLES["Storyteller"])
    min_s, max_s = LENGTHS.get(length_label, LENGTHS["Medium"])
    target = random.randint(min_s, max_s)

    seed_basis = f"{role}|{tone}|{fmt}|{length_label}|{creativity}|{user_text}"
    random.seed(hash(seed_basis) % (2**32))

    openings = {
        "Storyteller": "Once more, from the top: ",
        "Movie Director": "INT. ROOM – DAY. ",
        "Game Master": "You stand at the threshold: ",
        "UX Copywriter": "Here’s the value in plain language: ",
        "Debate Coach": "Thesis: ",
        "Travel Planner": "Your mini-itinerary: ",
        "Poet": "—",
        "Comedian": "So here’s the thing: "
    }
    base = openings.get(role, "") + user_text.strip()
    base = creative_variations(base, creativity)

    sentences = sentence_split(base)
    voice_hint = role_cfg["voice"]

    while len(sentences) < target:
        add = random.choice(role_cfg["quirks"]) if random.random() < 0.5 else random.choice([
            f"Tone: {tone.lower()}.",
            f"Format: {fmt.lower()}.",
            f"Focus on: {random.choice(['clarity','imagery','structure','momentum'])}.",
            f"Voice: {voice_hint.lower()}."
        ])
        sentences.append(add)

    text = ". ".join(sentences[:target]) + "."

    if extras.get("title"):
        title = f"{role} — {random.choice(['Concept','Draft','Sketch','Cut','Take'])}"
        text = f"{title}\n\n{text}"
    if extras.get("tldr"):
        text += "\n\nTL;DR: " + random.choice([
            "Keep it focused and vivid.",
            "Lead with benefits; close with momentum.",
            "Offer choices, show stakes, invite action."
        ])
    if extras.get("ideas3"):
        ideas = [
            "A surprising opening that re-frames the problem",
            "A contrast pair (before/after) to highlight value",
            "A closing beat that points to the next step"
        ]
        text += "\n\nThree ideas:\n" + "\n".join(f"- {i}" for i in ideas)
    if extras.get("next_prompt"):
        text += "\n\nNext prompt: Try refining the audience and constraints."

    text = stylize(text, fmt)
    text = apply_constraints(text, extras, fmt)
    return text


# ---------------------------
# Routes
# ---------------------------
@app.route("/")
def index():
    html = f"""
    <!doctype html>
    <html lang='en'>
    <head>
      <meta charset='utf-8'>
      <title>Role-based Creative Chatbot</title>
    </head>
    <body style='font-family:Arial;max-width:800px;margin:40px auto;'>
      <h1>Role-based Creative Chatbot</h1>
      <form id='form'>
        <label>Role:</label>
        <select id='role'>{''.join(f"<option>{r}</option>" for r in ROLES)}</select><br><br>
        <label>Tone:</label>
        <select id='tone'>{''.join(f"<option>{t}</option>" for t in TONES)}</select><br><br>
        <label>Format:</label>
        <select id='format'>{''.join(f"<option>{f}</option>" for f in FORMATS)}</select><br><br>
        <label>Length:</label>
        <select id='length'><option>Short</option><option selected>Medium</option><option>Long</option></select><br><br>
        <label>Creativity:</label>
        <input type='range' id='creativity' min='0' max='1' step='0.05' value='0.5' /><span id='cval'>0.5</span><br><br>
        <textarea id='prompt' rows='5' cols='70' placeholder='Enter your idea...'></textarea><br><br>
        <button type='button' onclick='send()'>Generate</button>
      </form>
      <pre id='output' style='white-space:pre-wrap;background:#f4f4f4;padding:10px;border-radius:8px;'></pre>
      <script>
        const slider=document.getElementById('creativity');
        const cval=document.getElementById('cval');
        slider.oninput=()=>cval.textContent=slider.value;
        async function send(){{
          const data={{role:role.value,tone:tone.value,format:format.value,length:length.value,creativity:parseFloat(creativity.value),text:prompt.value,extras:{{}}}};
          const res=await fetch('/chat',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(data)}});
          const j=await res.json();
          document.getElementById('output').textContent=j.reply;
        }}
      </script>
    </body></html>
    """
    return render_template_string(html)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    role = data.get("role", "Storyteller")
    tone = data.get("tone", "Friendly")
    fmt = data.get("format", "Paragraph")
    length_label = data.get("length", "Medium")
    creativity = float(data.get("creativity", 0.5))
    user_text = (data.get("text") or "").strip()
    extras = data.get("extras") or {}

    if not user_text:
        return jsonify({"reply": "Please provide a prompt to write about."})

    reply = generate_response(role, tone, user_text, fmt, length_label, creativity, extras)
    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
