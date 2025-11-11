from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

INDEX_HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Role-based Creative Chatbot (Instant)</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    :root{--bg:#0b0d10;--panel:#12161c;--soft:#1b212a;--text:#e7ecf3;--muted:#a9b7c6}
    body{margin:0;background:var(--bg);color:var(--text);font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif}
    header{padding:18px 22px;border-bottom:1px solid #202833;background:var(--panel);position:sticky;top:0}
    h1{margin:0;font-size:18px;letter-spacing:.2px}
    .wrap{display:grid;grid-template-columns:360px 1fr;gap:16px;padding:16px;max-width:1200px;margin:0 auto}
    .card{background:var(--panel);border:1px solid #202833;border-radius:14px;padding:14px}
    label{display:block;font-size:12px;color:var(--muted);margin-top:8px}
    select,input[type=range],textarea{width:100%;background:var(--soft);color:var(--text);border:1px solid #263142;border-radius:10px;padding:10px;outline:none}
    textarea{min-height:120px;resize:vertical}
    .row{display:grid;grid-template-columns:1fr 1fr;gap:8px}
    .opts{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:8px}
    .check{display:flex;gap:8px;align-items:center;font-size:13px;color:var(--muted)}
    .btn{margin-top:12px;padding:12px 14px;background:#2b82f6;border:none;color:#fff;border-radius:10px;cursor:pointer;font-weight:600}
    .btn:disabled{opacity:.6;cursor:not-allowed}
    .chat{display:flex;flex-direction:column;gap:12px}
    .bubble{background:var(--panel);border:1px solid #202833;border-radius:12px;padding:12px;white-space:pre-wrap}
    .meta{font-size:12px;color:var(--muted);margin-bottom:6px}
    pre{white-space:pre-wrap;margin:0}
    footer{color:#8190a6;font-size:12px;text-align:center;padding:10px}
  </style>
</head>
<body>
  <header><h1>Role-based Creative Chatbot (Client-side, instant)</h1></header>
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

      <div class="opts">
        <div class="check"><input type="checkbox" id="title"><span>Include title</span></div>
        <div class="check"><input type="checkbox" id="tldr"><span>Include TL;DR</span></div>
        <div class="check"><input type="checkbox" id="ideas3"><span>Add 3 ideas</span></div>
        <div class="check"><input type="checkbox" id="next_prompt"><span>Suggest next prompt</span></div>
        <div class="check"><input type="checkbox" id="no_emojis"><span>No emojis</span></div>
        <div class="check"><input type="checkbox" id="force_bullets"><span>Force bullets</span></div>
        <div class="check"><input type="checkbox" id="quote"><span>Include a quote</span></div>
        <div class="check"><input type="checkbox" id="cta"><span>Include a CTA</span></div>
      </div>

      <button class="btn" id="send">Generate</button>
    </div>

    <div class="card">
      <div class="chat" id="chat"></div>
    </div>
  </div>
  <footer>No network calls required. Output is generated instantly in your browser.</footer>

  <script>
    // --- Roles, tones, formats (English) ---
    const ROLES = {
      "Storyteller": {
        voice: "Warm, vivid, descriptive. Uses narrative arcs and sensory detail.",
        quirks: [
          "Weave a hook in the opening line.",
          "Add a subtle twist near the end.",
          "Use one metaphor, not more."
        ]
      },
      "Movie Director": {
        voice: "Cinematic, scene-driven, visual blocking and camera cues.",
        quirks: [
          "Stage each beat like a shot list.",
          "Include sound design hints.",
          "End with a cut-to-black moment."
        ]
      },
      "Game Master": {
        voice: "Interactive, second-person, offers choices and consequences.",
        quirks: [
          "Present at least two branching options.",
          "Describe environment with one tactical detail.",
          "Invite the next action."
        ]
      },
      "UX Copywriter": {
        voice: "Clear, concise, benefit-first with microcopy polish.",
        quirks: [
          "Lead with a user benefit.",
          "Use active voice.",
          "End with a crisp CTA."
        ]
      },
      "Debate Coach": {
        voice: "Structured, steelman opposing views, emphasizes logic and evidence.",
        quirks: [
          "State thesis in one line.",
          "List strongest counterpoint fairly.",
          "Conclude with action-oriented takeaway."
        ]
      },
      "Travel Planner": {
        voice: "Friendly, practical, locally-savvy with quick tips.",
        quirks: [
          "Add time-of-day suggestions.",
          "Note one money-saving tip.",
          "Include a photo-worthy stop."
        ]
      },
      "Poet": {
        voice: "Rhythmic, image-rich, compact lines.",
        quirks: [
          "Keep lines under twelve words.",
          "Use one surprising image.",
          "Close with a soft echo."
        ]
      },
      "Comedian": {
        voice: "Light, observational humor with a gentle punchline.",
        quirks: [
          "Set up → misdirection → payoff.",
          "One self-aware aside.",
          "Keep it kind, not cruel."
        ]
      }
    };
    const TONES = ["Friendly", "Professional", "Playful", "Dramatic", "Inspiring", "Neutral"];
    const FORMATS = ["Paragraph", "Bulleted List", "Outline", "Dialogue"];
    const LENGTHS = { Short:[4,6], Medium:[7,11], Long:[12,18] };

    // --- DOM ---
    const roleSel = document.getElementById('role');
    const toneSel = document.getElementById('tone');
    const fmtSel  = document.getElementById('format');
    const lenSel  = document.getElementById('length');
    const cRange  = document.getElementById('creativity');
    const cVal    = document.getElementById('cval');
    const promptEl= document.getElementById('prompt');
    const chatEl  = document.getElementById('chat');
    const sendBtn = document.getElementById('send');

    Object.keys(ROLES).forEach(r=>{ const o=document.createElement('option'); o.textContent=r; roleSel.appendChild(o); });
    TONES.forEach(t=>{ const o=document.createElement('option'); o.textContent=t; toneSel.appendChild(o); });
    FORMATS.forEach(f=>{ const o=document.createElement('option'); o.textContent=f; fmtSel.appendChild(o); });

    cRange.addEventListener('input', ()=> cVal.textContent = cRange.value);

    // --- Helpers ---
    const splitSentences = (t)=> t.replace(/\n/g,' ').split('.').map(s=>s.trim()).filter(Boolean);
    const clamp = (n,a,b)=> Math.max(a,Math.min(b,n));

    function creative(base, creativity){
      const pool = ["crisp","velvet","luminous","tactile","whispering","electric","quiet","bold","nuanced","sparkling","grainy","sleek","playful","intense"];
      const k = clamp(Math.floor(creativity*5),0,5);
      if(k>0){
        const picks = pool.sort(()=>0.5-Math.random()).slice(0,k);
        base += " " + picks.join(", ") + ".";
      }
      return base;
    }

    function stylize(text, fmt){
      const s = splitSentences(text);
      if(fmt==="Paragraph") return s.join('. ') + '.';
      if(fmt==="Bulleted List") return s.map(x=>"• "+x+".").join("\n");
      if(fmt==="Outline") return s.map((x,i)=> (i+1)+". "+x+".").join("\n");
      if(fmt==="Dialogue"){
        const speakers=["You","Bot"];
        return s.map((x,i)=> speakers[i%2]+": "+x+".").join("\n");
      }
      return text;
    }

    function applyExtras(text, extras, fmt){
      if(extras.no_emojis) text = [...text].filter(ch=>/[\x00-\x7F]/.test(ch)).join('');
      if(extras.force_bullets && fmt!=="Bulleted List"){
        const lines = splitSentences(text);
        text = lines.map(l=>"• "+l).join("\n");
      }
      if(extras.quote){
        const q = ["Simplicity sharpens ideas.","Contrast creates clarity.","Small steps compound into journeys."];
        text += "\n\n“"+ q[Math.floor(Math.random()*q.length)] +"”";
      }
      if(extras.cta) text += "\n\n→ Try it now and share your next prompt.";
      return text;
    }

    function generate(role, tone, userText, fmt, lengthLabel, creativityVal, extras){
      const cfg = ROLES[role] || ROLES["Storyteller"];
      const [minS,maxS] = LENGTHS[lengthLabel] || LENGTHS.Medium;
      const target = Math.floor(Math.random()*(maxS-minS+1))+minS;

      const openings = {
        "Storyteller": "Once more, from the top: ",
        "Movie Director": "INT. ROOM – DAY. ",
        "Game Master": "You stand at the threshold: ",
        "UX Copywriter": "Here’s the value in plain language: ",
        "Debate Coach": "Thesis: ",
        "Travel Planner": "Your mini-itinerary: ",
        "Poet": "—",
        "Comedian": "So here’s the thing: "
      };
      let base = (openings[role]||"") + userText.trim();
      base = creative(base, creativityVal);

      const sentences = splitSentences(base);
      const voice = cfg.voice.toLowerCase();
      while(sentences.length < target){
        const add = (Math.random()<0.5)
          ? cfg.quirks[Math.floor(Math.random()*cfg.quirks.length)]
          : ["Tone: "+tone.toLowerCase()+".",
             "Format: "+fmt.toLowerCase()+".",
             "Focus on: "+["clarity","imagery","structure","momentum"][Math.floor(Math.random()*4)]+".",
             "Voice: "+voice+"."][Math.floor(Math.random()*4)];
        sentences.push(add);
      }

      let text = sentences.slice(0,target).join(". ") + ".";
      if(extras.title){
        const t = role+" — "+["Concept","Draft","Sketch","Cut","Take"][Math.floor(Math.random()*5)];
        text = t + "\n\n" + text;
      }
      if(extras.tldr){
        const lines = [
          "Keep it focused and vivid.",
          "Lead with benefits; close with momentum.",
          "Offer choices, show stakes, invite action."
        ];
        text += "\n\nTL;DR: " + lines[Math.floor(Math.random()*lines.length)];
      }
      if(extras.ideas3){
        text += "\n\nThree ideas:\n- A surprising opening that re-frames the problem\n- A contrast pair (before/after) to highlight value\n- A closing beat that points to the next step";
      }
      if(extras.next_prompt){
        text += "\n\nNext prompt: Try refining the audience and constraints.";
      }

      text = stylize(text, fmt);
      text = applyExtras(text, extras, fmt);
      return text;
    }

    function addBubble(text, who){
      const wrap = document.createElement('div');
      wrap.className = 'bubble';
      const meta = document.createElement('div'); meta.className='meta'; meta.textContent = who==='user'?'You':'Bot';
      const pre = document.createElement('pre'); pre.textContent = text;
      wrap.appendChild(meta); wrap.appendChild(pre);
      chatEl.appendChild(wrap);
      chatEl.scrollTop = chatEl.scrollHeight;
    }

    sendBtn.addEventListener('click', ()=>{
      const input = promptEl.value.trim();
      if(!input){ addBubble('(Please type something to generate.)','bot'); return; }
      addBubble(input,'user');
      const payload = {
        role: roleSel.value,
        tone: toneSel.value,
        fmt: fmtSel.value,
        len: lenSel.value,
        creativity: parseFloat(cRange.value),
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
      const reply = generate(payload.role, payload.tone, input, payload.fmt, payload.len, payload.creativity, payload.extras);
      addBubble(reply,'bot');
    });
  </script>
</body>
</html>"""

@app.route("/")
def index():
    return render_template_string(INDEX_HTML)

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    # 0.0.0.0 便于容器/云环境；如平台要求自定义端口，可改成 os.getenv("PORT", 5000)
    app.run(host="0.0.0.0", port=5000, debug=False)
