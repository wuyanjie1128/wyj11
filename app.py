# app.py
# Role-based Creative Chatbot (English UI)
# Streamlit web app with rich controls, presets, expandables, safe-text guardrails,
# export/import of settings and transcripts, and multi-step creative "modes".
#
# NOTE: This app is fully local and does NOT call any external APIs.

import json
import random
import re
import textwrap
from datetime import datetime
from typing import Dict, List

import streamlit as st

# ----------------------------
# App Config
# ----------------------------
st.set_page_config(
    page_title="Role-based Creative Chatbot",
    page_icon="🎭",
    layout="wide"
)

# Seed once for reproducibility across a session
if "seed" not in st.session_state:
    st.session_state.seed = random.randint(1, 10_000)
random.seed(st.session_state.seed)

# ----------------------------
# Utilities
# ----------------------------
def clamp(n, lo, hi):
    return max(lo, min(hi, n))

def split_sentences(text: str) -> List[str]:
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    return [p for p in parts if p]

def stylize_text(text: str, device_pack: Dict[str, bool], role_voice: Dict[str, str], creativity: float) -> str:
    """Apply literary devices and role-specific flavor in a deterministic-but-playful way."""
    lines = split_sentences(text) or [text]
    out = []

    # device toggles
    use_alliteration = device_pack.get("Alliteration", False)
    use_metaphor = device_pack.get("Metaphor", False)
    use_rule_of_three = device_pack.get("Rule of Three", False)
    use_rhetorical_q = device_pack.get("Rhetorical Questions", False)
    use_sensory = device_pack.get("Sensory Details", False)

    # role tone hints
    prefix = role_voice.get("prefix", "")
    postfix = role_voice.get("postfix", "")
    synonyms_boost = role_voice.get("synonyms", [])
    cadence = role_voice.get("cadence", "neutral")

    # Simple synonym substitution bank (kept small and safe)
    base_synonyms = {
        "good": ["solid", "compelling", "engaging", "persuasive"],
        "great": ["remarkable", "outstanding", "stellar", "exceptional"],
        "fast": ["swift", "rapid", "quick"],
        "slow": ["unhurried", "measured", "gradual"],
        "beautiful": ["elegant", "graceful", "stunning"],
        "strong": ["robust", "resilient", "powerful"],
        "simple": ["straightforward", "clean", "uncluttered"],
        "complex": ["intricate", "multi-layered", "nuanced"],
        "idea": ["concept", "angle", "approach", "direction"],
        "story": ["narrative", "tale", "arc", "chronicle"],
        "user": ["audience", "reader", "player", "viewer"]
    }

    # blend role synonyms
    for k, vals in list(base_synonyms.items()):
        if synonyms_boost:
            base_synonyms[k] = list(dict.fromkeys(vals + synonyms_boost))

    def maybe_synonym(word: str) -> str:
        if random.random() > creativity:
            return word
        key = word.lower()
        if key in base_synonyms:
            choice = random.choice(base_synonyms[key])
            return choice if word.islower() else choice.capitalize()
        return word

    def device_alliteration(sentence: str) -> str:
        if not use_alliteration:
            return sentence
        # pick a letter and try to alliterate beginning words
        letter = random.choice(list("bcdfghjklmnpqrstvwxyz"))
        words = sentence.split()
        for i in range(min(3, len(words))):
            if len(words[i]) > 3:
                words[i] = f"{letter}{words[i][1:]}"
        return " ".join(words)

    def device_metaphor(sentence: str) -> str:
        if not use_metaphor or len(sentence) < 10:
            return sentence
        metaphors = [
            "like a compass in a crowded bazaar",
            "as if stitched from midnight and neon",
            "like a lighthouse cutting fog",
            "as steady as a heartbeat drum",
            "like sparks skipping across water"
        ]
        if random.random() < creativity:
            return sentence + " " + random.choice(metaphors) + "."
        return sentence

    def device_rule_of_three(sentence: str) -> str:
        if not use_rule_of_three:
            return sentence
        # append a triad if short
        triads = [
            "clarity, momentum, and intent",
            "setup, escalation, and payoff",
            "hook, heart, and hindsight",
            "discover, design, and deliver"
        ]
        if len(sentence) < 140 and random.random() < 0.6:
            return sentence.rstrip(".") + f" — {random.choice(triads)}."
        return sentence

    def device_rhetorical(sentence: str) -> str:
        if not use_rhetorical_q or len(sentence) < 40:
            return sentence
        qs = [
            "What if we leaned into the tension?",
            "Is there a sharper hook we can try?",
            "What would delight the audience the most?"
        ]
        if random.random() < creativity * 0.7:
            return sentence + " " + random.choice(qs)
        return sentence

    def device_sensory(sentence: str) -> str:
        if not use_sensory:
            return sentence
        spices = [
            "You can almost hear the soft hum beneath it.",
            "You can feel the cool edge of the idea in your palm.",
            "There’s a citrus brightness in the momentum.",
            "It carries the warm grain of daylight."
        ]
        if random.random() < creativity * 0.5:
            return sentence + " " + random.choice(spices)
        return sentence

    # cadence
    def apply_cadence(text: str) -> str:
        if cadence == "punchy":
            return re.sub(r',', ' —', text)
        elif cadence == "lyrical":
            return text.replace(".", ".")
        return text

    for s in lines:
        # synonym pass
        words = re.findall(r"\w+|[^\w\s]", s, re.UNICODE)
        words = [maybe_synonym(w) if w.isalpha() else w for w in words]
        s2 = "".join([w if re.match(r"[^\w\s]", w) else (" " + w if i else w) for i, w in enumerate(words)])
        # devices
        s2 = device_alliteration(s2)
        s2 = device_metaphor(s2)
        s2 = device_rule_of_three(s2)
        s2 = device_rhetorical(s2)
        s2 = device_sensory(s2)
        s2 = apply_cadence(s2)
        out.append(s2)

    text = " ".join(out)
    text = (prefix + " " + text + " " + postfix).strip()
    return text

def safety_guard(text: str) -> bool:
    """Simple guardrail to refuse unsafe categories; extend as needed."""
    blocked = [
        r"\bviolence\b", r"\bself[-\s]?harm\b", r"\bsuicide\b",
        r"\bterror\b", r"\bexplosive\b", r"\bhate\b"
    ]
    for pat in blocked:
        if re.search(pat, text, flags=re.I):
            return False
    return True

def clean_prompt(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()

# ----------------------------
# Roles & Modes
# ----------------------------
ROLE_LIBRARY: Dict[str, Dict] = {
    "Screenwriter": {
        "desc": "Structure scenes, beats, and dialogue with cinematic pacing.",
        "voice": {"prefix": "INT. CREATIVE STUDIO — DAY.", "postfix": "", "synonyms": ["scene", "beat", "stakes"], "cadence": "punchy"},
    },
    "Marketing Strategist": {
        "desc": "Positioning, value props, and copy that converts without fluff.",
        "voice": {"prefix": "From a strategist’s desk:", "postfix": "Let’s move.", "synonyms": ["conversion", "resonance", "friction"], "cadence": "neutral"},
    },
    "UX Writer": {
        "desc": "Microcopy and flows that reduce friction and increase clarity.",
        "voice": {"prefix": "On-screen guidance:", "postfix": "", "synonyms": ["clarity", "flow", "coherence"], "cadence": "punchy"},
    },
    "Children’s Author": {
        "desc": "Gentle rhythms, bright images, and friendly wonder.",
        "voice": {"prefix": "Once upon a soft morning,", "postfix": "", "synonyms": ["friend", "giggle", "wonder"], "cadence": "lyrical"},
    },
    "Sci-Fi Worldbuilder": {
        "desc": "Big ideas, lived-in details, and plausible systems.",
        "voice": {"prefix": "In a near-future skyline,", "postfix": "", "synonyms": ["protocol", "orbit", "biosphere"], "cadence": "neutral"},
    },
    "Poet Laureate": {
        "desc": "Concise imagery, sonic texture, and layered meaning.",
        "voice": {"prefix": "", "postfix": "", "synonyms": ["lilt", "cadence", "echo"], "cadence": "lyrical"},
    },
    "Game Narrative Designer": {
        "desc": "Quests, lore, and choice consequences with playful hooks.",
        "voice": {"prefix": "Quest Log Update:", "postfix": "", "synonyms": ["quest", "faction", "artifact"], "cadence": "punchy"},
    },
    "Data Storyteller": {
        "desc": "Turn numbers into narrative arcs and human insights.",
        "voice": {"prefix": "From the dataset:", "postfix": "", "synonyms": ["signal", "variance", "pattern"], "cadence": "neutral"},
    },
    "Motivational Coach": {
        "desc": "Supportive, actionable, forward energy (wellbeing-safe).",
        "voice": {"prefix": "You’ve got this.", "postfix": "One focused step at a time.", "synonyms": ["momentum", "commitment", "progress"], "cadence": "punchy"},
    },
    "Stand-up Comedian (clean)": {
        "desc": "Light observational humor with clean language.",
        "voice": {"prefix": "So get this:", "postfix": "", "synonyms": ["bit", "riff", "callback"], "cadence": "punchy"},
    },
}

CREATIVE_MODES = {
    "Brainstorm": "Generate many short ideas with tags.",
    "Outline": "Produce a structured outline (I/II/III).",
    "Draft": "Write a coherent draft with sections.",
    "Rewrite": "Rewrite input text in the selected role.",
    "Summarize": "Summarize and highlight action points."
}

OUTPUT_FORMS = ["General prose", "Taglines", "Bullet list", "Poem", "Microcopy", "Ad copy", "Social thread", "Pitch paragraph"]

DEVICE_OPTIONS = ["Alliteration", "Metaphor", "Rule of Three", "Rhetorical Questions", "Sensory Details"]

LENGTH_MAP = {
    "Very short": (60, 100),
    "Short": (120, 200),
    "Medium": (220, 400),
    "Long": (500, 800)
}

# ----------------------------
# Sidebar Controls
# ----------------------------
with st.sidebar:
    st.header("Choose a Role 🎭")
    role_name = st.selectbox("Role", list(ROLE_LIBRARY.keys()), index=1, help="Select a creative persona.")

    st.header("Creative Mode 🧪")
    mode_name = st.selectbox("Mode", list(CREATIVE_MODES.keys()), index=0, help=CREATIVE_MODES)

    st.header("Output Controls 🛠️")
    out_form = st.selectbox("Output form", OUTPUT_FORMS, index=0)
    length_label = st.selectbox("Length", list(LENGTH_MAP.keys()), index=2)
    min_chars, max_chars = LENGTH_MAP[length_label]
    creativity = st.slider("Creativity (0 = literal, 1 = wild)", 0.0, 1.0, 0.55, 0.05)
    temperature = st.slider("Variety (higher = more varied phrasing)", 0.0, 1.0, 0.5, 0.05)

    st.header("Constraints & Audience 🎯")
    target_audience = st.text_input("Target audience (optional)", value="general audience")
    required_keywords = st.text_input("Required keywords (comma-separated)", value="")
    taboo_words = st.text_input("Banned words (comma-separated)", value="")
    pov = st.selectbox("Point of view", ["First person", "Second person", "Third person"], index=1)

    st.header("Style Devices ✨")
    device_pack = {}
    for opt in DEVICE_OPTIONS:
        device_pack[opt] = st.checkbox(opt, value=(opt in ["Metaphor", "Rule of Three"]))

    st.header("Advanced 🔧")
    wrap_width = st.number_input("Wrap width (characters)", min_value=60, max_value=140, value=100, step=2)
    max_ideas = st.slider("Idea count (Brainstorm)", 3, 12, 6, 1)
    bullet_prefix = st.text_input("Bullet prefix", value="• ")

    st.header("Presets & Export 📦")
    colA, colB = st.columns(2)
    with colA:
        export_btn = st.button("Export Settings", use_container_width=True)
    with colB:
        export_chat_btn = st.button("Export Transcript", use_container_width=True)
    imported = st.file_uploader("Import settings (.json)", type=["json"])

# ----------------------------
# Session State
# ----------------------------
if "transcript" not in st.session_state:
    st.session_state.transcript = []

def add_turn(role: str, user: str, bot: str):
    st.session_state.transcript.append({
        "time": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "role": role,
        "user": user,
        "bot": bot
    })

# Handle exports
if export_btn:
    cfg = {
        "role_name": role_name,
        "mode_name": mode_name,
        "out_form": out_form,
        "length_label": length_label,
        "creativity": creativity,
        "temperature": temperature,
        "target_audience": target_audience,
        "required_keywords": required_keywords,
        "taboo_words": taboo_words,
        "pov": pov,
        "device_pack": device_pack,
        "wrap_width": wrap_width,
        "max_ideas": max_ideas,
        "bullet_prefix": bullet_prefix,
        "seed": st.session_state.seed
    }
    st.download_button(
        label="Download settings.json",
        data=json.dumps(cfg, indent=2),
        file_name="settings.json",
        mime="application/json"
    )

if export_chat_btn:
    text_dump = []
    for t in st.session_state.transcript:
        text_dump.append(f"[{t['time']}] ROLE={t['role']}\nUSER: {t['user']}\nBOT: {t['bot']}\n")
    st.download_button(
        label="Download transcript.txt",
        data="\n".join(text_dump),
        file_name="transcript.txt",
        mime="text/plain"
    )

if imported is not None:
    try:
        cfg = json.load(imported)
        # Soft-apply: show as info (safer than hot-overwriting widgets mid-run)
        st.success("Settings imported. Please re-select values to mirror imported config:")
        st.json(cfg, expanded=False)
    except Exception as e:
        st.error(f"Failed to import: {e}")

# ----------------------------
# Main UI
# ----------------------------
st.title("Role-based Creative Chatbot")
st.caption("Pick a role, choose a mode, and craft nuanced creative outputs—right in your browser.")

colL, colR = st.columns([1, 2])

with colL:
    st.markdown("### Prompt")
    user_prompt = st.text_area(
        "Describe what you want:",
        height=160,
        placeholder="E.g., Launch announcement for a minimalist note-taking app focused on calm productivity."
    )
    run = st.button("Generate", type="primary", use_container_width=True)

with colR:
    st.markdown("### About this Role")
    st.write(f"**{role_name}** — {ROLE_LIBRARY[role_name]['desc']}")
    st.markdown(f"**Mode:** {mode_name} · **Form:** {out_form} · **Length:** {length_label}")
    st.info("Tip: use the left panel to tune creativity, devices, audience, and constraints. Export your settings or transcript any time.")

st.markdown("---")

# ----------------------------
# Core Generation (local, deterministic-ish)
# ----------------------------
def apply_constraints(text: str, req_kw: str, taboo: str) -> str:
    # Ensure required keywords appear; if not, weave them in at the end.
    musts = [k.strip() for k in req_kw.split(",") if k.strip()]
    bans = [b.strip().lower() for b in taboo.split(",") if b.strip()]
    base = text

    if musts:
        missing = [m for m in musts if re.search(re.escape(m), base, re.I) is None]
        if missing:
            base += "\n\nRequired notes: " + "; ".join(missing) + "."
    if bans:
        for b in bans:
            base = re.sub(fr"\b{re.escape(b)}\b", "[redacted]", base, flags=re.I)
    return base

def pov_transform(text: str, pov_choice: str) -> str:
    # Lightweight POV tweak; (doesn't rewrite pronouns perfectly, just adds perspective framing)
    if pov_choice == "First person":
        return "From my perspective: " + text
    if pov_choice == "Second person":
        return "For you, consider this: " + text
    return text  # Third person neutral

def brainstorm_blocks(topic: str, ideas: int, role_voice, form, bullet_prefix: str) -> str:
    pool_tags = ["hook", "angle", "tension", "benefit", "tw
