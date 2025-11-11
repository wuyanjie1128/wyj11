# app.py

```python
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
LENGTHS = {
    "Short": (4, 6),
    "Medium": (7, 11),
    "Long": (12, 18)
}

# ---------------------------
# Text helpers (simple, no external APIs)
# ---------------------------

def sentence_split(text):
    parts = [p.strip() for p in text.replace("\n", " ").split(".")]
    return [p for p in parts if p]


def clamp(n, a, b):
    return max(a, min(b, n))


def apply_constraints(text, constraints):
    if constraints.get("no_emojis"):
        # Naive emoji strip
        text = ''.join(ch for ch in text if ch.isascii())
    if constraints.get("bullets") and constraints.get("format") != "Bulleted List":
        # Add bullets if requested explicitly
        lines = sentence_split(text)
        text = "\n".join(f"• {line}" for line in lines)
    if constraints.get("quote_one_line"):
        text += "\n\n\"" + random.choice([
            "Simplicity sharpens ideas.",
            "Contrast creates clarity.",
            "Small steps compound into journeys."
        ]) + "\""
    if constraints.get("cta"):
        text += "\n\n→ Try it now and share your next prompt."
    return text


def stylize(text, fmt):
    if fmt == "Paragraph":
        return textwrap.fill(text, width=90)
    if fmt == "Bulleted List":
        parts = sentence_split(text)
        return "\n".join(f"• {p}." for p in parts)
    if fmt == "Outline":
        parts = sentence_split(text)
        out = []
        for i, p in enumerate(parts, 1):
            out.append(f"{i}. {p}.")
        return "\n".join(out)
    if fmt == "Dialogue":
        parts = sentence_split(text)
        speakers = ["You", "Bot"]
        lines = []
        for i, p in enumerate(parts):
            lines.append(f"{speakers[i % 2]}: {p}.")
        return "\n".join(lines)
    return text


def creative_variations(base, creativity):
    # Adds small vivid details and synonyms based on creativity 0..1
    spice_pool = [
        "crisp", "velvet", "luminous", "tactile", "whispering", "electric", "quiet",
        "bold", "nuanced", "sparkling", "grainy", "sleek", "playful", "intense"
    ]
    k = clamp(int(creativity * 5), 0, 5)
    choices = random.sample(spice_pool, k) if k else []
    if choices:
        base += " " + ", ".join(choices) + "."
    return base


def generate_response(role, tone, user_text, fmt, length_label, creativity, extras):
    role_cfg = ROLES.get(role, ROLES["Storyteller"])
    min_s, max_s = LENGTHS.get(length_label, LENGTHS["Medium"])
    target = random.randint(min_s, max_s)

    # Seed so same input yields stable-ish output per request
    seed_basis = f"{role}|{tone}|{fmt}|{length_label}|{creativity}|{user_text}"
    random.seed(hash(seed_basis) % (2**32))

    # Build a prompt skeleton (rule-based for reliability)
    opening = {
        "Storyteller": "Once more, from the top: ",
        "Movie Director": "INT. ROOM – DAY. ",
        "Game Master": "You stand at the threshold: ",
        "UX Copywriter": "Here’s the value in plain language: ",
        "Debate Coach": "Thesis: ",
        "Travel Planner": "Your mini-itinerary: ",
        "Poet": "—",
        "Comedian": "So here’s the thing: "
    }.get(role, "")

    base = f"{opening}{user_text.strip()}"
    base = creative_variations(base, creativity)

    # Draft sentences
    sentences = sentence_split(base)
    voice_hint = role_cfg["voice"]

    while len(sentences) < target:
        add = random.choice(role_cfg["quirks"]) if random.random() < 0.5 else random.choice([
            f"Tone: {tone.lower()}.",
            f"Format: {fmt.lower()}.",
            f"Focus on: {random.choice(['clarity', 'imagery', 'structure', 'momentum'])}.",
            f"Consider: {random.choice(['audience needs', 'pacing', 'contrast', 'voice'])}.",
            f"Voice: {voice_hint.lower()}"
        ])
        sentences.append(add)

    text = ". ".join(sentences[:target]) + "."

    # Extras
    if extras.get("title"):
        title = f"{role} — {random.choice(['Concept', 'Draft', 'Sketch', 'Cut', 'Take'])}"
        text = f"{title}\n\n" + text
    if extras.get("tldr"):
        text += "\n\nTL;DR: " + random.choice([
            "Keep it focused, vivid, and audience-first.",
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

    # Apply format and constraints last
    text = stylize(text, fmt)
    text = apply_constraints(text, {
        "no_emojis": extras.get("no_emojis", False),
        "bullets": extras.get("force_bullets", False),
        "quote_one_line": extras.get("quote", False),
        "cta": extras.get("cta", False),
        "format": fmt
    })

    return text

# ---------------------------
# Routes
# ---------------------------
INDEX_HTML = """
<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Role‑based Creative Chatbot</title>
  <style>
    :root { --bg:#0b0d10; --panel:#12161c; --soft:#1b212a; --text:#e7ecf3; --muted:#a9b7c6; }
    body { margin:0; font-family:system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; background:var(--bg); color:var(--text); }
    header { padding:20px 24px; border-bottom:1px solid #202833; background:var(--panel); position:sticky; top:0; z-index:2; }
    h1 { margin:0; font-size:20px; letter-spacing:.3px; }
    .wrap { display:grid; grid-template-columns: 360px 1fr; gap:16px; padding:16px; }
    .card { background:var(--panel); border:1px solid #202833; border-radius:14px; padding:14px; }
    label { display:block; font-size:12px; color:var(--muted); margin-top:8px; }
    select, input[type=range], textarea, input[type=text] { width:100%; background:var(--soft); color:var(--text); border:1px solid #263142; border-radius:10px; padding:10px; outline:none; }
    textarea { min-height:120px; resize:vertical; }
    .row { display:grid; grid-template-columns: 1fr 1fr; gap:8px; }
    .btn { margin-top:12px; padding:12px 14px; background:#2b82f6; border:none; color:#fff; border-radius:10px; cursor:pointer; font-weight:600; }
    .btn:disabled { opacity:.6; cursor:not-allowed; }
    .chat { display:flex; flex-direction:column; gap:12px; }
    .bubble { background:var(--panel); border:1px solid #202833; border-radius:12px; padding:12px; white-space:pre-wrap; }
    .bubble.user { background:#17202b; }
    .meta { font-size:12px; color:var(--muted); margin-bottom:6px; }
    .opts { display:grid; grid-template-columns: 1fr 1fr; gap:8px; }
    .check { display:flex; gap:8px; align-items:center; font-size:13px; color:var(--muted); }
    footer { text-align:center; color:#8190a6; font-size:12px; padding:12px; }
  </style>
</head>
<body>
  <header><h1>Role‑based Creative Chatbot</h1></header>
  <div class="wrap">
    <div class="card">
      <div class="row">
        <div>
          <label>Choose a role</label>
          <select id="role"></select>
        </div>
        <div>
          <label>Tone</label>
          <select id="tone"></select>
        </div>
      </div>

      <div class="row" style="margin-top:8px;">
        <div>
          <label>Format</label>
          <select id="format"></select>
        </div>
        <div>
          <label>Response length</label>
          <select id="length">
            <option>Short</option>
            <option selected>Medium</option>
            <option>Long</option>
          </select>
        </div>
      </div>

      <label style="margin-top:10px;">Creativity: <span id="cval">0.5</span></label>
      <input id="creativity" type="range" min="0" max="1" step="0.05" value="0.5" />

      <label style="margin-top:10px;">Your prompt</label>
      <textarea id="prompt" placeholder="Describe what you want..."></textarea>

      <div class="opts" style="margin-top:8px;">
        <div class="check"><input type="checkbox" id="title"/><span>Include title</span></div>
        <div class="check"><input type="checkbox" id="tldr"/><span>Include TL;DR</span></div>
        <div class="check"><input type="checkbox" id="ideas3"/><span>Add 3 ideas</span></div>
        <div class="check"><input type="checkbox" id="next_prompt"/><span>Suggest next prompt</span></div>
        <div class="check"><input type="checkbox" id="no_emojis"/><span>No emojis</span></div>
        <div class="check"><input type="checkbox" id="force_bullets"/><span>Force bullets</span></div>
        <div class="check"><input type="checkbox" id="quote"/><span>Include a quote</span></div>
        <div class="check"><input type="checkbox" id="cta"/><span>Include a CTA</span></div>
      </div>

      <button class="btn" id="send">Generate</button>
    </div>

    <div class="card">
      <div class="chat" id="chat"></div>
    </div>
  </div>
  <footer>No external AI calls. Fully local, deterministic-ish output.</footer>

  <script>
    const ROLES = %ROLES_JSON%;
    const TONES = %TONES_JSON%;
    const FORMATS = %FORMATS_JSON%;

    const roleSel = document.getElementById('role');
    const toneSel = document.getElementById('tone');
    const fmtSel  = document.getElementById('format');
    const chatEl = document.getElementById('chat');
    const cRange = document.getElementById('creativity');
    const cVal = document.getElementById('cval');

    // Populate selects
    Object.keys(ROLES).forEach(r => {
      const o = document.createElement('option'); o.textContent = r; roleSel.appendChild(o);
    });
    TONES.forEach(t => { const o = document.createElement('option'); o.textContent = t; toneSel.appendChild(o); });
    FORMATS.forEach(f => { const o = document.createElement('option'); o.textContent = f; fmtSel.appendChild(o); });

    cRange.addEventListener('input', () => cVal.textContent = cRange.value);

    function addBubble(text, who){
      const wrap = document.createElement('div');
      wrap.className = 'bubble' + (who==='user' ? ' user' : '');
      const meta = document.createElement('div'); meta.className='meta'; meta.textContent = who==='user' ? 'You' : 'Bot';
      const pre = document.createElement('pre'); pre.style.whiteSpace='pre-wrap'; pre.textContent = text;
      wrap.appendChild(meta); wrap.appendChild(pre);
      chatEl.appendChild(wrap);
      chatEl.scrollTop = chatEl.scrollHeight;
    }

    document.getElementById('send').addEventListener('click', async () => {
      const prompt = document.getElementById('prompt').value.trim();
      if(!prompt){ return; }
      addBubble(prompt, 'user');
      const btn = document.getElementById('send'); btn.disabled = true; btn.textContent='Generating…';
      try{
        const payload = {
          role: roleSel.value,
          tone: toneSel.value,
          format: fmtSel.value,
          length: document.getElementById('length').value,
          creativity: parseFloat(cRange.value),
          text: prompt,
          extras: {
            title: document.getElementById('title').checked,
            tldr: document.getElementById('tldr').checked,
            ideas3: document.getElementById('ideas3').checked,
            next_prompt: document.getElementById('next_prompt').checked,
            no_emojis: document.getElementById('no_emojis').checked,
            force_bullets: document.getElementById('force_bullets').checked,
            quote: document.getElementById('quote').checked,
            cta: document.getElementById('cta').checked
          }
        };
        const res = await fetch('/chat', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)});
        const data = await res.json();
        addBubble(data.reply, 'bot');
      } catch(err){
        addBubble('Oops—something went wrong, but the app itself is running. Try again.', 'bot');
        console.error(err);
      } finally {
        btn.disabled = false; btn.textContent='Generate';
      }
    });
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    # Bake small JSON blobs into the template for robust, single-file deploys
    import json
    html = INDEX_HTML.replace("%ROLES_JSON%", json.dumps(ROLES)) \
                     .replace("%TONES_JSON%", json.dumps(TONES)) \
                     .replace("%FORMATS_JSON%", json.dumps(FORMATS))
    return render_template_string(html)


@app.route("/chat", methods=["POST"])
def chat():
    try:
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
    except Exception as e:
        # Fail safe: never crash the server; return a graceful message instead.
        return jsonify({"reply": f"The request could not be processed safely. Error class: {type(e).__name__}. Please adjust inputs and try again."}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
```

---

# requirements.txt

```
Flask>=3.0.0
```
