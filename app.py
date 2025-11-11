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

# ---------------------------
# Title and Description
# ---------------------------
st.title("🎭 Role-based Creative Chatbot")
st.write(
    "Welcome! This is an interactive chatbot that can take on different creative roles — "
    "like a screenwriter, poet, marketer, or designer — and generate styled responses. "
    "No external API required!"
)

# ---------------------------
# Role Definitions
# ---------------------------
ROLES = {
    "Screenwriter": "Writes scenes and dialogues with cinematic pacing.",
    "Marketing Strategist": "Creates persuasive and catchy campaign ideas.",
    "UX Writer": "Focuses on clarity and user-friendly language.",
    "Poet": "Writes lyrical and emotional passages.",
    "Sci-Fi Author": "Imagines futuristic worlds and technologies.",
    "Comedian": "Adds humor and witty observations.",
    "Motivational Coach": "Provides encouragement and focus.",
    "Game Designer": "Designs lore, quests, and in-game text."
}

# ---------------------------
# Sidebar Controls
# ---------------------------
st.sidebar.header("⚙️ Chatbot Settings")

role = st.sidebar.selectbox("Choose a Role", list(ROLES.keys()), index=1)
tone = st.sidebar.selectbox("Tone", ["Neutral", "Friendly", "Inspirational", "Formal", "Playful"], index=2)
length = st.sidebar.selectbox("Response Length", ["Short", "Medium", "Long"], index=1)
creativity = st.sidebar.slider("Creativity Level", 0.0, 1.0, 0.6, 0.05)
style = st.sidebar.multiselect(
    "Writing Devices",
    ["Metaphor", "Alliteration", "Rule of Three", "Rhetorical Question", "Sensory Detail"],
    default=["Metaphor"]
)

st.sidebar.markdown("---")
st.sidebar.info("Adjust the style and tone, then enter your prompt below!")

# ---------------------------
# Helper Functions
# ---------------------------
def stylize_text(text: str) -> str:
    """Applies creative writing devices for stylistic variation."""
    if "Metaphor" in style and random.random() < creativity:
        text += " It’s like painting with light and shadow."
    if "Alliteration" in style and random.random() < creativity:
        text = text.replace("strong", "steady and sure")
    if "Rule of Three" in style and random.random() < creativity:
        text += " Focus, rhythm, and flow."
    if "Rhetorical Question" in style and random.random() < creativity:
        text += " What more could inspire creativity?"
    if "Sensory Detail" in style and random.random() < creativity:
        text += " You can almost feel the spark behind these words."
    return text

def generate_response(role, tone, text, creativity, length):
    """Generates styled text (no API required)."""
    if not text.strip():
        return "Please enter a prompt to start."

    intro_templates = [
        f"As a {role.lower()}, I'd say:",
        f"From a {role.lower()}'s point of view:",
        f"Here's how a {role.lower()} might respond:",
    ]
    intro = random.choice(intro_templates)

    multiplier = {"Short": 2, "Medium": 4, "Long": 6}[length]
    words = text.split()
    body_text = " ".join(words[: multiplier * 10])

    body = f"{body_text.capitalize()} — written in a {tone.lower()} tone."
    styled = stylize_text(body)
    wrapped = textwrap.fill(styled, width=90)

    return f"{intro}\n\n{wrapped}"

# ---------------------------
# User Input
# ---------------------------
st.subheader("💬 Enter your Prompt")
prompt = st.text_area("What do you want me to write about?", placeholder="e.g. A story about teamwork in space", height=150)

if st.button("✨ Generate Response", type="primary"):
    st.subheader(f"🧠 {role}'s Response")
    output = generate_response(role, tone, prompt, creativity, length)
    st.write(output)

# ---------------------------
# Footer
# ---------------------------
st.markdown("---")
st.caption(
    "This chatbot runs entirely on Streamlit — no external APIs or accounts needed. "
    "You can deploy it directly from GitHub to Streamlit Cloud."
)
