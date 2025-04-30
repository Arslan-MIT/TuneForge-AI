import streamlit as st
from openai import OpenAI
import requests
import os
from dotenv import load_dotenv

# Load keys from .env
# load_dotenv("key.env")  # Make sure your file is named correctly
st.set_page_config(page_title="AI Melody Maker", page_icon="🎵")

# --- API KEYS ---
#AIML_API_KEY = os.getenv("AIML_API_KEY")  # Use variable name, not actual key
AIML_API_KEY = '8f3498fe90434e61a5913cb35000b4ff'

if not AIML_API_KEY:
    st.error("❌ AIML_API_KEY not found. Make sure it's set in key.env.")
    st.stop()

# --- Initialize AI/ML GPT-4o client ---
try:
    aiml_api = OpenAI(
        api_key=AIML_API_KEY,
        base_url="https://api.aimlapi.com/v1"
    )
    st.info("✅ AIML API client initialized.")
except Exception as e:
    st.error(f"❌ Failed to initialize AIML API client: {e}")
    st.stop()

st.title("🎵 AI Melody Maker")
st.markdown("Generate **lyrics**, **melodies**, and **titles** with the power of Generative AI!")

# --- UI for inputs ---
mood = st.selectbox("Choose a mood", ["Happy", "Sad", "Chill", "Energetic"])
genre = st.selectbox("Choose a genre", ["Pop", "Hip Hop", "Classical", "EDM", "Rock"])
keywords = st.text_input("Enter keywords (optional)", placeholder="e.g., love, rain, party")

if st.button("Generate Song"):
    with st.spinner("Creating your AI song..."):
        st.info("🎤 Generating lyrics...")

        try:
            # --- Lyrics generation ---
            lyric_prompt = f"Write song lyrics in {genre} style with a {mood} mood. Use themes: {keywords or 'any'}."
            lyrics_result = aiml_api.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": lyric_prompt}],
                temperature=0.7,
                max_tokens=300
            )
            lyrics = lyrics_result.choices[0].message.content
            st.success("✅ Lyrics generated.")
        except Exception as e:
            st.error(f"❌ Failed to generate lyrics: {e}")
            st.stop()

        st.info("🧠 Generating title...")

        try:
            # --- Title suggestion ---
            title_prompt = f"Give a short, catchy title for this song: {lyrics}"
            title_result = aiml_api.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": title_prompt}],
                temperature=0.7,
                max_tokens=20
            )
            title = title_result.choices[0].message.content.strip().strip('"')
            st.success("✅ Title generated.")
        except Exception as e:
            st.error(f"❌ Failed to generate title: {e}")
            title = "Untitled"

        st.info("🎼 Generating melody...")

        # --- Melody Generation (Stable Audio) ---
        try:
            stable_headers = {
                "Authorization": f"Bearer {AIML_API_KEY}",
                "Content-Type": "application/json"
            }
            stable_payload = {
                "prompt": f"A {mood.lower()} {genre.lower()} melody about {keywords or 'anything'}",
                "duration": 10,
                "format": "wav"
            }

            response = requests.post(
                "https://api.stableaudio.com/v1/generate",
                headers=stable_headers,
                json=stable_payload
            )

            if response.status_code == 200:
                audio_url = response.json().get("audio_url")
                st.success("✅ Melody generated.")
            else:
                audio_url = None
                st.warning(f"⚠️ Melody generation failed. Status: {response.status_code}")
        except Exception as e:
            audio_url = None
            st.error(f"❌ Error while generating melody: {e}")

        # --- Display Results ---
        st.subheader("🎶 Title:")
        st.write(title)

        st.subheader("📝 Lyrics:")
        st.text(lyrics)

        if audio_url:
            st.subheader("🎧 Melody:")
            st.audio(audio_url)
            st.markdown(f"[⬇️ Download Melody]({audio_url})")
        else:
            st.warning("⚠️ No melody preview available.")

        st.download_button("📄 Download Lyrics", lyrics, file_name=f"{title}_lyrics.txt")
