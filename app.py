# app.py
# Role-based Creative Chatbot (English version)
# ✅ Fully self-contained, safe, deployable to Streamlit Cloud

import streamlit as st
import random
import textwrap

# ---------------------------
# Page setup
# ---------------------------
st.set_page_config(
    page_title="Role-based Creative Chatbot",
    page_icon="🎭",
    layout="wide"
)

st.title("🎭 Role-based Creative Chatbot")
st.caption("Choose a creative role, adjust style options, and generate text instantly — no API required!")

# ---------------------------
# Role Definitions
# ---------------------------
ROLES = {
    "Screenwriter": "Creates cinematic dialogue and story beats.",
    "Marketing Strategist": "Writes persuasive copy that drives action.",
    "UX Writer": "Focuses on clarity and user-friendly language.",
    "Poet": "Uses lyrical rhythm and emotional imagery.",
    "Sci-Fi Author": "Builds futuristic worlds and imaginative ideas.",
    "Comedian": "Writes humorous, lighthearted takes on any topic.",
    "Motivational Coach": "Encourages readers with supportive energy.",
    "Game Narrative Designer": "Crafts engaging quests and lore elements."
}

# ---------------------------
# Sidebar controls
# ---------------------------
st.sidebar.header("⚙️ Settings")

role = st.sidebar.selectbox("Choose a Role", list(ROLES.keys()), index=1)
tone = st.sidebar.selectbox("Tone", ["Neutral", "Friendly", "Inspirational", "Formal", "Playful"], index=2)
length = st.sidebar.selectbox("Response Length", ["Short", "Medium", "Long"], index=1)
creativity = st.sidebar.slider("Creativity Level", 0.0, 1.0, 0.6, 0.05)
style = st.sidebar.multiselect(
    "Writing Devices",
    ["Metaphor", "Alliteration", "Rule of Three", "Rhetorical Question", "Sensory Detail"],
    default=["Metaphor", "Rule of Three"]
)

st.sidebar.markdown("---")
st.sidebar.info("Adjust these settings, then enter your prompt below!")

# ---------------------------
# Helper functions
# ---------------------------
def stylize_text(text: str) -> str:
    """Add light creative devices to make text livelier."""
    if "Metaphor" in style and random.random() < creativity:
        text += " It’s like catching starlight in a jar."
    if "Alliteration" in style and random.random() < creativity:
        text = text.replace("strong", "swift and steady")
    if "Rule of Three" in style and random.random() < creativity:
        text += " Balance, rhythm, and resonance."
    if "Rhetorical Question" in style and random.random() < creativity:
        text += " What could be more exciting?"
    if "Sensory Detail" in style and random.random() < creativity:
        text += " You can almost feel the warmth behind the words."
    return text

def generate_response(role, tone, text, creativity, length):
    """Fake but elegant text generation logic."""
    if not text.strip():
        return "Please enter a prompt to start the conversation."

    base_templates = [
        f"As a {role.lower()}, I'd say:",
        f"From the {role.lower()}'s perspective:",
        f"Here's how a {role.lower()} might express that:",
        f"Through the lens of a {role.lower()}, consider this:"
    ]
    intro = random.choice(base_templates)

    multiplier = {"Short": 2, "Medium": 4, "Long": 6}[length]
    words = text.split()
    sentence = " ".join(words[: multiplier * 10])

    body = f"{sentence.capitalize()} — crafted with a {tone.lower()} tone."
    final = stylize_text(body)

    # Wrap lines for nice formatting
    return textwrap.fill(f"{intro}\n\n{final}", width=90)

# ---------------------------
# User Input
# ---------------------------
st.markdown("### 💬 Enter your prompt")
prompt = st.text_area("What should I write about?", placeholder="e.g. A story about teamwork in space", height=150)

if st.button("✨ Generate Response", type="primary", use_container_width=True):
    st.subheader(f"🧠 {role}'s Response")
    output = generate_response(role, tone, prompt, creativity, length)
    st.write(output)

# ---------------------------
# Footer
# ---------------------------
st.markdown("---")
st.caption(
    "This creative chatbot runs entirely in your browser using Streamlit. "
    "It does not connect to any external API or store data. "
    "Feel free to fork and customize it on GitHub!"
)
