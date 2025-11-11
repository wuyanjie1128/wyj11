import streamlit as st
import random
import re
from datetime import datetime
from textwrap import shorten

# -----------------------------
# App Config
# -----------------------------
st.set_page_config(
    page_title="Role-based Creative Chatbot",
    page_icon="🎭",
    layout="wide",
)

# -----------------------------
# Utilities
# -----------------------------
def init_state():
    if "history" not in st.session_state:
        st.session_state.history = []  # list of dicts: {"role": "user/assistant/system", "content": str, "meta": dict}
    if "seed" not in st.session_state:
        st.session_state.seed = 42
    if "rng" not in st.session_state:
        st.session_state.rng = random.Random(st.session_state.seed)
    if "active_role" not in st.session_state:
        st.session_state.active_role = "Novelist"
    if "system_persona" not in st.session_state:
        st.session_state.system_persona = ""

def now_iso():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def maybe_bulletize(text, line_max=140):
    # Light bulletizer if the text looks like a list prompt
    items = re.split(r"[;\n]+", text.strip())
    items = [i.strip() for i in items if i.strip()]
    if len(items) >= 3 and all(len(i) <= line_max for i in items):
        return "\n".join([f"- {i}" for i in items])
    return text

# -----------------------------
# Role Catalog & Behaviors
# -----------------------------
ROLE_DEFS = {
    "Novelist": {
        "style": "vivid imagery, character-driven, varied sentence length, occasional metaphor",
        "tools": ["Outline", "Beat Sheet", "Character Sketch", "Plot Twist"],
        "tones": ["Warm", "Dark", "Epic", "Whimsical", "Bittersweet"],
    },
    "Poet": {
        "style": "lyrical, compressed imagery, attention to rhythm and sound",
        "tools": ["Haiku", "Free Verse", "Pantoum-ish", "Ekphrasis"],
        "tones": ["Tender", "Melancholic", "Playful", "Surreal"],
    },
    "Screenwriter": {
        "style": "cinematic, visual blocking, dialog-forward, sluglines",
        "tools": ["Logline", "Beat Sheet", "Scene", "Dialogue Polish"],
        "tones": ["Gritty", "Witty", "High-stakes", "Deadpan"],
    },
    "Game Master": {
        "style": "interactive narration, second-person cues, crunchy details, hooks",
        "tools": ["World Builder", "Encounter", "Item Generator", "NPC"],
        "tones": ["Heroic", "Cozy", "Horror", "Sword & Sorcery"],
    },
    "Marketer": {
        "style": "benefit-led, crisp copy, CTA-aware, audience targeting",
        "tools": ["Tagline", "Value Props", "Landing Section", "Ad Variants"],
        "tones": ["Bold", "Trustworthy", "Friendly", "Premium"],
    },
    "UX Writer": {
        "style": "clear, concise, helpful, inclusive, action-oriented",
        "tools": ["Microcopy", "Empty State", "Onboarding", "Error Message"],
        "tones": ["Reassuring", "Neutral", "Upbeat", "Expert"],
    },
    "Teacher": {
        "style": "scaffolding, analogies, step-by-step, Socratic prompts",
        "tools": ["Lesson Plan", "Explain Like I'm 5", "Quiz", "Assignment"],
        "tones": ["Encouraging", "Rigorous", "Patient", "Curious"],
    },
    "Comedian": {
        "style": "observational, misdirection, call-backs, rhythm",
        "tools": ["One-liners", "Premise → Punchline", "Roast (wholesome)", "Sketch idea"],
        "tones": ["Deadpan", "Absurd", "Self-deprecating", "Satirical"],
    },
    "Data Storyteller": {
        "style": "insight-first, narrative arc, chart suggestions, comparisons",
        "tools": ["Hook", "Executive Summary", "Slide Outline", "Headline Variants"],
        "tones": ["Neutral", "Optimistic", "Urgent", "Balanced"],
    },
}

# Built-in “plugins”: small, deterministic creative helpers
def plugin_world_builder(rng, theme, detail):
    seeds = [
        f"A wind-worn port city built on basalt cliffs, famous for {detail} and markets that open before dawn.",
        f"A floating archipelago of libraries where knowledge is taxed in hours of sleep—{detail} is the black market.",
        f"A subterranean orchard lit by bioluminescent vines; {detail} is a rite of passage.",
        f"A desert monastery whose bells summon rain; {detail} is carved into every threshold.",
    ]
    return rng.choice(seeds).replace("{detail}", theme)

def plugin_character_forge(rng, occupation, flaw):
    traits = ["meticulous", "mercurial", "stoic", "improvisational", "soft-spoken", "incorrigibly curious"]
    hooks = [
        "owes a life-debt to a rival",
        "collects forbidden maps",
        "cannot cross bridges at dawn",
        "writes letters to a future self",
        "savors silence like tea",
    ]
    return f"{rng.choice(traits)} {occupation} who {rng.choice(hooks)}; main flaw: {flaw}."

def plugin_plot_twist(rng):
    twists = [
        "The mentor is a decoy; the real guide has been the antagonist’s diary.",
        "The map is a memory palace—whoever holds it forgets what they love.",
        "The prophecy was a product roadmap; the ‘chosen one’ is a usability test.",
        "The monster is hibernating under the city’s music hall.",
        "The priceless artifact is a replica; the box is the real treasure.",
    ]
    return rng.choice(twists)

def plugin_scamper(rng, topic):
    frames = [
        ("Substitute", f"What if {topic} were replaced with its opposite?"),
        ("Combine", f"What if {topic} merged with a daily ritual?"),
        ("Adapt", f"What can we borrow from aviation for {topic}?"),
        ("Modify", f"If we exaggerate one property of {topic}, what breaks first?"),
        ("Put to other use", f"Where could {topic} work in a hospital?"),
        ("Eliminate", f"What happens if we remove onboarding from {topic}?"),
        ("Reverse", f"What if {topic} starts at the end and works backward?"),
    ]
    rng.shuffle(frames)
    return "\n".join([f"- **{k}:** {v}" for k, v in frames])

def plugin_haiku(rng, theme):
    line1 = rng.choice(["Autumn traffic hums", "Glass rivers at dawn", "Sunlit code unfolds"])
    line2 = rng.choice([f"{theme} in a teacup storm", f"footnotes of the sky", f"quiet commits bloom"])
    line3 = rng.choice(["we learn to wait well", "pixels breathe like moss", "wind signs the release"])
    return f"{line1}\n{line2}\n{line3}"

def plugin_taglines(rng, product, tone):
    starts = {
        "Bold": ["Own the moment.", "Make noise.", "Be unmistakable."],
        "Friendly": ["Hello, easy.", "Nice to meet better.", "Small steps, big smiles."],
        "Premium": ["Simply elevated.", "Crafted to last.", "Rarer. Smarter. Yours."],
        "Trustworthy": ["Built on better.", "Count on clarity.", "Because details matter."],
        "Neutral": ["Do more with less.", "Made to work.", "It just helps."],
    }
    lines = starts.get(tone, starts["Neutral"])
    add = [
        f"{product}, without the hassle.",
        f"{product} that feels like tomorrow.",
        f"{product}—because time is the real luxury.",
    ]
    rng.shuffle(add)
    return "\n".join([rng.choice(lines), add[0]])

# -----------------------------
# Generation Core (deterministic-ish)
# -----------------------------
def generate_creative_reply(
    rng,
    role,
    user_text,
    tone="Neutral",
    length="Medium",
    structure="Auto",
    constraints=None,
    persona_notes="",
    style_guide="",
    temperature=0.5,
    allow_lists=True,
):
    """
    A lightweight, deterministic creative engine (no external APIs).
    Uses templates + shuffling + plugins to transform input into role-flavored output.
    """
    constraints = constraints or []
    words = user_text.strip()
    if not words:
        words = "Create something delightful about nothing in particular."

    # Base envelope by role
    flavor = ROLE_DEFS.get(role, ROLE_DEFS["Novelist"])
    style = flavor["style"]

    # Token-ish shuffler to mimic temperature
    tok = re.split(r"(\s+)", words)
    k = clamp(int(len(tok) * (temperature * 0.25)), 0, max(0, len(tok) - 1))
    if k > 2:
        rng.shuffle(tok[:k])
    remixed = "".join(tok).strip()

    # Length control
    length_map = {
        "Very Short": (40, 80),
        "Short": (80, 140),
        "Medium": (140, 220),
        "Long": (220, 400),
        "Very Long": (400, 800),
    }
    lo, hi = length_map.get(length, (140, 220))

    # Structure selection
    structures = {
        "Auto": ["Paragraph", "Bulleted", "Outline"],
        "Paragraph": ["Paragraph"],
        "Bulleted": ["Bulleted"],
        "Outline": ["Outline"],
        "Dialogue": ["Dialogue"],
        "Scene": ["Scene"],
    }
    chosen_struct = rng.choice(structures.get(structure, ["Paragraph"]))

    # Compose header
    header = f"**Role:** {role}  •  **Tone:** {tone}  •  **Style:** {style}"
    if persona_notes:
        header += f"\n**Persona notes:** {persona_notes}"
    if constraints:
        header += f"\n**Constraints:** {', '.join(constraints)}"
    if style_guide:
        header += f"\n**Style Guide:** {shorten(style_guide, width=140, placeholder='…')}"

    # Body builders per structure
    def build_paragraph():
        body = (
            f"In a {tone.lower()} register, consider this: {remixed}. "
            f"Focus on clarity and momentum. Add sensory detail when helpful, avoid filler. "
            f"Keep {role.lower()} conventions in mind."
        )
        if allow_lists and rng.random() < 0.25:
            body += "\n\nKey beats:\n- Setup\n- Turn\n- Payoff"
        return body

    def build_bulleted():
        base = maybe_bulletize(remixed)
        lines = base.splitlines()
        bullets = []
        for ln in lines:
            ln = ln.strip(" -")
            if ln:
                bullets.append(f"- {ln}")
        if not bullets:
            bullets = [f"- {remixed}"]
        bullets += ["- Tension rises", "- A choice must be made", "- Consequence lands"]
        return "\n".join(bullets)

    def build_outline():
        return "\n".join(
            [
                "I. Hook — an image or a promise",
                f"II. Context — {remixed}",
                "III. Complication — stakes sharpen",
                "IV. Decision — irreversible choice",
                "V. Outcome — satisfying yet open",
            ]
        )

    def build_dialogue():
        return "\n".join(
            [
                "A: I thought the plan was simple.",
                f"B: It was, until {remixed}.",
                "A: Then we improvise.",
                "B: That’s not improvisation; that’s honesty with a deadline.",
            ]
        )

    def build_scene():
        return "\n".join(
            [
                "INT. QUIET ROOM – EVENING",
                f"Soft light. A notebook open. On the page: “{remixed}”.",
                "A kettle clicks. Someone exhales like a page turning.",
                "They underline a word, not to cage it—just to notice.",
            ]
        )

    builders = {
        "Paragraph": build_paragraph,
        "Bulleted": build_bulleted,
        "Outline": build_outline,
        "Dialogue": build_dialogue,
        "Scene": build_scene,
    }
    body = builders.get(chosen_struct, build_paragraph)()

    # Enforce approximate length by additive padding/trim
    if len(body) < lo:
        pad = " " + " ".join(
            rng.choice(
                [
                    "Add a tangible detail.",
                    "Offer a contrast.",
                    "Use a sharp verb.",
                    "Tighten the rhythm.",
                    "Name what changes.",
                ]
            )
            for _ in range(max(1, (lo - len(body)) // 24))
        )
        body += pad
    elif len(body) > hi:
        body = body[:hi] + "…"

    return header + "\n\n" + body

# -----------------------------
# Sidebar — Controls
# -----------------------------
init_state()

with st.sidebar:
    st.header("🎭 Choose a role")
    role = st.selectbox("Role", list(ROLE_DEFS.keys()), index=list(ROLE_DEFS.keys()).index(st.session_state.active_role))
    st.session_state.active_role = role

    st.markdown("**Tone**")
    tone = st.select_slider("Pick a tone", options=ROLE_DEFS[role]["tones"], value=ROLE_DEFS[role]["tones"][0])

    st.markdown("**Structure**")
    structure = st.selectbox(
        "Preferred structure",
        ["Auto", "Paragraph", "Bulleted", "Outline", "Dialogue", "Scene"],
        index=0
    )

    st.markdown("**Length**")
    length = st.select_slider("Target length", options=["Very Short", "Short", "Medium", "Long", "Very Long"], value="Medium")

    st.markdown("**Advanced**")
    temperature = st.slider("Creativity (pseudo temperature)", 0.0, 1.0, 0.55, 0.05)
    allow_lists = st.checkbox("Allow list inserts / beats", True)
    memory_on = st.checkbox("Conversation memory (use previous turns)", True)
    st.session_state.seed = st.number_input("Random seed (deterministic runs)", min_value=0, value=42, step=1)
    st.session_state.rng = random.Random(st.session_state.seed)

    st.markdown("---")
    st.subheader("🧩 Plugins")
    colp1, colp2 = st.columns(2)
    with colp1:
        wb_enabled = st.checkbox("World Builder", False)
        char_enabled = st.checkbox("Character Forge", False)
        twist_enabled = st.checkbox("Plot Twist", False)
    with colp2:
        scamper_enabled = st.checkbox("SCAMPER Ideation", False)
        haiku_enabled = st.checkbox("Haiku", False)
        tagline_enabled = st.checkbox("Taglines", False)

    st.markdown("---")
    st.subheader("✍️ Persona & Style")
    persona_notes = st.text_area("Persona notes (voice, audience, POV)", "")
    style_guide = st.text_area("Style guide (do/don’t, terminology)", "")

    st.markdown("---")
    st.subheader("🔎 Prompt inspector")
    show_inspector = st.checkbox("Show composed system/context prompt", False)

    st.markdown("---")
    st.subheader("⬇️ Export")
    if st.session_state.history:
        transcript = "\n".join(
            f"[{h['meta'].get('ts','')}] {h['role'].upper()}: {h['content']}"
            for h in st.session_state.history
        ).encode("utf-8")
        st.download_button("Download conversation (.txt)", transcript, "chat_transcript.txt", "text/plain")

# -----------------------------
# Main Header
# -----------------------------
st.title("Role-based Creative Chatbot")
st.caption("A detailed, extensible creative assistant with role selection, plugins, persona controls, and safe offline generation.")

# Instruction card
with st.expander("What can this do?", expanded=True):
    st.markdown(
        """
**Pick a role** in the sidebar, set a tone/structure/length, tweak creativity, then chat below.  
Enable **plugins** (World Builder, Character Forge, Plot Twist, SCAMPER, Haiku, Taglines) for extra flavor.  
Use **Persona & Style** to shape the voice; turn on **Conversation memory** to let replies build on prior turns.
        """
    )

# -----------------------------
# Prompt Inspector (shows context)
# -----------------------------
if show_inspector:
    sys_preview = f"""SYSTEM CONTEXT
Role: {role}
Tone: {tone}
Structure: {structure}
Length: {length}
Temperature: {temperature}
Allow Lists: {allow_lists}
Persona Notes: {persona_notes or "(none)"}
Style Guide: {style_guide or "(none)"}
Plugins: {", ".join([p for p, on in [
    ("World Builder", wb_enabled), ("Character Forge", char_enabled), ("Plot Twist", twist_enabled),
    ("SCAMPER", scamper_enabled), ("Haiku", haiku_enabled), ("Taglines", tagline_enabled)] if on]) or "(none)"}"""
    st.code(sys_preview, language="markdown")

# -----------------------------
# Chat Area
# -----------------------------
chat_container = st.container()

# Display history
with chat_container:
    for h in st.session_state.history:
        with st.chat_message(h["role"]):
            st.markdown(h["content"])

# User input
user_input = st.chat_input("Type your prompt (e.g., 'Write an opening scene on a rainy spaceport')")

def build_memory_prefix():
    """Lightweight summary of recent conversation to simulate memory."""
    if not st.session_state.history:
        return ""
    # Use last 4 exchanges
    recent = st.session_state.history[-8:]
    lines = []
    for h in recent:
        tag = "U" if h["role"] == "user" else "A"
        lines.append(f"{tag}: {shorten(h['content'], width=120, placeholder='…')}")
    return "Conversation memory:\n" + "\n".join(lines) + "\n\n"

if user_input:
    # Record user turn
    st.session_state.history.append({"role": "user", "content": user_input, "meta": {"ts": now_iso(), "role": role}})

    # Compose extra plugin outputs
    rng = st.session_state.rng
    plugin_bits = []

    if wb_enabled:
        plugin_bits.append("**World Builder:** " + plugin_world_builder(rng, theme=user_input, detail="ancient trade routes"))
    if char_enabled:
        plugin_bits.append("**Character Forge:** " + plugin_character_forge(rng, occupation="smuggler-archivist", flaw="impatient with ambiguity"))
    if twist_enabled:
        plugin_bits.append("**Plot Twist:** " + plugin_plot_twist(rng))
    if scamper_enabled:
        plugin_bits.append("**SCAMPER:**\n" + plugin_scamper(rng, topic=user_input))
    if haiku_enabled:
        plugin_bits.append("**Haiku:**\n" + plugin_haiku(rng, theme=user_input))
    if tagline_enabled:
        plugin_bits.append("**Taglines:**\n" + plugin_taglines(rng, product=user_input, tone=tone))

    plugin_section = "\n\n".join(plugin_bits)

    # Memory prefix
    prefix = build_memory_prefix() if memory_on else ""

    # Generate reply
    reply = generate_creative_reply(
        rng=rng,
        role=role,
        user_text=prefix + user_input,
        tone=tone,
        length=length,
        structure=structure,
        constraints=[],
        persona_notes=persona_notes,
        style_guide=style_guide,
        temperature=temperature,
        allow_lists=allow_lists,
    )

    if plugin_section:
        reply = reply + "\n\n---\n" + plugin_section

    # Append assistant turn
    st.session_state.history.append({"role": "assistant", "content": reply, "meta": {"ts": now_iso(), "role": role}})

    # Display immediately
    with chat_container:
        with st.chat_message("assistant"):
            st.markdown(reply)

# Footer
st.markdown("---")
st.caption("This app uses deterministic templates and randomization (no external APIs), so it runs anywhere Streamlit runs.")
