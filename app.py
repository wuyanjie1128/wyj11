from flask import Flask, request, jsonify, render_template_string
import random
import textwrap

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
LENGTHS = {"Short": (4, 6), "Medium": (7, 11), "Long": (12, 18)}

# ---------------------------
# Helpers
# ---------------------------
def sentence_split(text: str):
    parts = [p.strip() for p in text.replace("\n", " ").split(".")]
    return [p for p in parts if p]

def clamp(n, a, b):
    return max(a, min(b, n))

def creative_variations(base: str, creativity: float) -> str:
    spice_pool = [
        "crisp", "velvet", "luminous", "tactile", "whispering",
        "electric", "quiet", "bold", "nuanced", "sparkling", "grainy", "sleek"
    ]
    k = clamp(int(creativity * 5), 0, 5)
    choices = random.sample(spice_pool, k) if k else []
    if choices:
        base += " " + ", ".join(choices) + "."
    return base

def stylize(text: str, fmt: str) -> str:
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
        return "\n".join(f"{speakers[i % 2]}: {p}." for i, p in enumerate(parts))
    return text

def apply_constraints(text: str, extras: dict, fmt: str) -> str:
    if extras.get("no_emojis"):
        text = "".join(ch for ch in text if ch.isascii())
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

    # seed for stability
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
    # keep HTML ultra-simple; no external files
    html = f"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Role-based Creative Chatbot</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
</head>
<body style="font-family:Arial,Helvetica,sans-serif;max-width:900px;margin:40px auto;line-height:1.35">
  <h1>Role-based Creative Chatbot</h1>

  <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
    <label>Role
      <select id="role">{''.join(f'<option>{r}</option>' for r in ROLES.keys())}</select>
    </label>
    <label>Tone
      <select id="tone">{''.join(f'<option>{t}</option>' for t in TONES)}</select>
    </label>
    <label>Format
      <select id="fmt">{''.join(f'<option>{f}</option>' for f in FORMATS)}</select>
    </label>
    <label>Length
      <select id="length"><option>Short</option><option selected>Medium</option><option>Long</option></select>
    </label>
  </div>

  <label style="display:block;margin-top:10px;">Creativity:
    <input type="range" id="creativity" min="0" max="1" step="0.05" value="0.5" />
    <b id="cval">0.5</b>
  </label>

  <textarea id="prompt" rows="6" style="width:100%;margin-top:10px;" placeholder="Describe what you want..."></textarea>

  <fieldset style="margin-top:10px;">
    <legend>Extras</legend>
    <label><input type="checkbox" id="title"> Include title</label>
    <label><input type="checkbox" id="tldr"> Include TL;DR</label>
    <label><input type="checkbox" id="ideas3"> Add 3 ideas</label>
    <label><input type="checkbox" id="next_prompt"> Suggest next prompt</label>
    <label><input type="checkbox" id="no_emojis"> No emojis</label>
    <label><input type="checkbox" id="force_bullets"> Force bullets</label>
    <label><input type="checkbox" id="quote"> Include a quote</label>
    <label><input type="checkbox" id="cta"> Include a CTA</label>
  </fieldset>

  <button id="go" style="margin-top:12px;padding:10px 14px;">Generate</button>

  <pre id="out" style="white-space:pre-wrap;background:#f6f8fa;border:1px solid #e1e4e8;border-radius:8px;padding:12px;margin-top:12px;"></pre>

  <script>
    const el = (id) => document.getElementById(id);
    const role = el('role');
    const tone = el('tone');
    const fmt = el('fmt');
    const lengthSel = el('length');
    const creativity = el('creativity');
    const cval = el('cval');
    const promptBox = el('prompt');
    const out = el('out');
    const go = el('go');

    creativity.addEventListener('input', () => cval.textContent = creativity.value);

    async function generate() {{
      const payload = {{
        role: role.value,
        tone: tone.value,
        format: fmt.value,
        length: lengthSel.value,
        creativity: parseFloat(creativity.value),
        text: promptBox.value,
        extras: {{
          title: el('title').checked,
          tldr: el('tldr').checked,
          ideas3: el('ideas3').checked,
          next_prompt: el('next_prompt').checked,
          no_emojis: el('no_emojis').checked,
          force_bullets: el('force_bullets').checked,
          quote: el('quote').checked,
          cta: el('cta').checked
        }}
      }};
      try {{
        go.disabled = true; go.textContent = 'Generating...';
        const res = await fetch('/chat', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify(payload)
        }});
        const data = await res.json();
        out.textContent = data.reply || '(No reply)';
      }} catch (e) {{
        out.textContent = 'Request failed. See console for details.';
        console.error(e);
      }} finally {{
        go.disabled = false; go.textContent = 'Generate';
      }}
    }}

    go.addEventListener('click', generate);
  </script>
</body>
</html>
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

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    # host=0.0.0.0 便于容器/远程环境访问；debug=False 保证稳定
    app.run(host="0.0.0.0", port=5000, debug=False)
