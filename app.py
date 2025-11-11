from flask import Flask, request, render_template_string
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
        "electric", "quiet", "bold", "nuanced", "sparkling", "grainy", "sleek", "playful", "intense"
    ]
    k = clamp(int(creativity * 5), 0, 5)
    if k > 0:
        choices = random.sample(spice_pool, k)
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

def apply_extras(text: str, extras: dict, fmt: str) -> str:
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

    # seed for stability per input
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
    base = openings.get(role, "") + (user_text or "").strip()
    if not base:
        base = openings.get(role, "") + "Write a short creative piece about a cozy café brand tagline."
    base = creative_variations(base, creativity)

    sentences = sentence_split(base)
    voice_hint = role_cfg["voice"].lower()

    while len(sentences) < target:
        add = random.choice(role_cfg["quirks"]) if random.random() < 0.5 else random.choice([
            f"Tone: {tone.lower()}.",
            f"Format: {fmt.lower()}.",
            f"Focus on: {random.choice(['clarity','imagery','structure','momentum'])}.",
            f"Voice: {voice_hint}."
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
        text += "\n\nThree ideas:\n- A surprising opening that re-frames the problem\n- A contrast pair (before/after) to highlight value\n- A closing beat that points to the next step"
    if extras.get("next_prompt"):
        text += "\n\nNext prompt: Try refining the audience and constraints."

    text = stylize(text, fmt)
    text = apply_extras(text, extras, fmt)
    return text

# ---------------------------
# Template (server-side only, no JS)
# ---------------------------
PAGE_TMPL = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Role-based Creative Chatbot (Server-rendered, instant)</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;max-width:1000px;margin:24px auto;padding:0 16px;color:#0b1320}
    .grid{display:grid;grid-template-columns:340px 1fr;gap:16px}
    .card{border:1px solid #e3e7ee;border-radius:12px;padding:14px}
    label{display:block;font-size:12px;color:#5a6b87;margin-top:8px}
    select,input[type=range],textarea{width:100%;border:1px solid #cfd6e0;border-radius:10px;padding:10px}
    textarea{min-height:120px}
    .row{display:grid;grid-template-columns:1fr 1fr;gap:8px}
    .opts{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:8px}
    .btn{margin-top:12px;padding:12px 14px;background:#2b82f6;border:none;color:#fff;border-radius:10px;cursor:pointer;font-weight:600}
    pre{white-space:pre-wrap;background:#f7f9fc;border:1px solid #e3e7ee;border-radius:10px;padding:12px}
    .muted{color:#6e7f9a;font-size:12px}
  </style>
</head>
<body>
  <h1>Role-based Creative Chatbot</h1>
  <p class="muted">Server-rendered only — opens with an instant sample. Adjust options and click <b>Generate</b>.</p>

  <div class="grid">
    <div class="card">
      <form method="post">
        <div class="row">
          <div>
            <label>Choose a role</label>
            <select name="role">
              {% for r in roles %}
                <option value="{{r}}" {% if r==role %}selected{% endif %}>{{r}}</option>
              {% endfor %}
            </select>
          </div>
          <div>
            <label>Tone</label>
            <select name="tone">
              {% for t in tones %}
                <option value="{{t}}" {% if t==tone %}selected{% endif %}>{{t}}</option>
              {% endfor %}
            </select>
          </div>
        </div>

        <div class="row" style="margin-top:8px;">
          <div>
            <label>Format</label>
            <select name="format">
              {% for f in formats %}
                <option value="{{f}}" {% if f==fmt %}selected{% endif %}>{{f}}</option>
              {% endfor %}
            </select>
          </div>
          <div>
            <label>Response length</label>
            <select name="length">
              {% for l in ['Short','Medium','Long'] %}
                <option value="{{l}}" {% if l==length_label %}selected{% endif %}>{{l}}</option>
              {% endfor %}
            </select>
          </div>
        </div>

        <label style="margin-top:10px;">Creativity: <b>{{creativity}}</b></label>
        <input name="creativity" type="range" min="0" max="1" step="0.05" value="{{creativity}}" />

        <label style="margin-top:10px;">Your prompt</label>
        <textarea name="text" placeholder="Describe what you want...">{{text}}</textarea>

        <div class="opts">
          {% for key,label in [
            ('title','Include title'),
            ('tldr','Include TL;DR'),
            ('ideas3','Add 3 ideas'),
            ('next_prompt','Suggest next prompt'),
            ('no_emojis','No emojis'),
            ('force_bullets','Force bullets'),
            ('quote','Include a quote'),
            ('cta','Include a CTA')
          ] %}
          <label><input type="checkbox" name="{{key}}" {% if extras.get(key) %}checked{% endif %}> {{label}}</label>
          {% endfor %}
        </div>

        <button class="btn" type="submit">Generate</button>
      </form>
    </div>

    <div class="card">
      <div class="muted">Output</div>
      <pre>{{reply}}</pre>
    </div>
  </div>
</body>
</html>
"""

# ---------------------------
# Routes
# ---------------------------
def parse_extras(form):
    keys = ["title","tldr","ideas3","next_prompt","no_emojis","force_bullets","quote","cta"]
    return {k: (k in form) for k in keys}

@app.route("/", methods=["GET", "POST"])
def index():
    # defaults ensure "instant" first render
    role = request.form.get("role") or "Storyteller"
    tone = request.form.get("tone") or "Friendly"
    fmt = request.form.get("format") or "Paragraph"
    length_label = request.form.get("length") or "Medium"
    try:
        creativity = float(request.form.get("creativity") or 0.5)
    except ValueError:
        creativity = 0.5
    text = request.form.get("text") or "Write a short creative piece about a cozy café brand tagline."

    extras = parse_extras(request.form) if request.method == "POST" else {
        "title": True, "tldr": True, "ideas3": False, "next_prompt": True,
        "no_emojis": False, "force_bullets": False, "quote": False, "cta": False
    }

    reply = generate_response(role, tone, text, fmt, length_label, creativity, extras)

    return render_template_string(
        PAGE_TMPL,
        roles=list(ROLES.keys()),
        tones=TONES,
        formats=FORMATS,
        role=role, tone=tone, fmt=fmt, length_label=length_label,
        creativity=creativity, text=text, extras=extras, reply=reply
    )

@app.route("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    # Use PORT env if provided by hosting platforms; fall back to 5000.
    import os
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)
